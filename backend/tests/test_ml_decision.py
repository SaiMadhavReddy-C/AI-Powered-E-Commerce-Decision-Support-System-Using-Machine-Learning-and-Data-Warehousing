"""Comprehensive test suite for ShopQ ML prediction models, Hard BUY safety gates,
Confidence engine, and Structured Decision synthesis.
"""

from datetime import datetime, timezone, timedelta
import pytest
import numpy as np

from app.schemas.product import (
    PriceHistoryPointSchema,
    ProductDetailSchema,
    RetailerListingSchema,
    SellerOfferSchema,
)
from app.schemas.offer import BestOfferSchema, CompetitorOfferSchema
from app.services.ml.data_prep import (
    clean_price_history,
    build_supervised_dataset,
    temporal_train_val_test_split,
    extract_features_at_step,
    FEATURE_NAMES,
)
from app.services.ml.predictor import price_predictor
from app.services.decision.safety_gate import safety_gate, HardBuySafetyGate
from app.services.decision.confidence_engine import confidence_engine, ConfidenceEngine
from app.services.decision.synthesizer import decision_synthesizer, DecisionSynthesizer
from app.services.decision_service import decision_service
from app.services.product_service import product_service


# =====================================================================
# 1. ML Model Strategy & Temporal Leakage Prevention Tests
# =====================================================================

def test_ml_data_prep_temporal_split_no_leakage():
    """Verifies that train/val/test split is strictly chronological (Past -> Train, Later -> Val, Newest -> Test)."""
    n = 100
    X = np.arange(n).reshape(-1, 1)
    y = np.arange(n)

    X_train, y_train, X_val, y_val, X_test, y_test = temporal_train_val_test_split(
        X, y, train_ratio=0.70, val_ratio=0.15
    )

    # Train max index < Val min index
    assert np.max(y_train) < np.min(y_val), "Train contains future indices relative to Val!"
    # Val max index < Test min index
    assert np.max(y_val) < np.min(y_test), "Val contains future indices relative to Test!"
    # No overlapping indices
    train_set = set(y_train.tolist())
    val_set = set(y_val.tolist())
    test_set = set(y_test.tolist())
    assert len(train_set.intersection(val_set)) == 0
    assert len(val_set.intersection(test_set)) == 0


def test_ml_supervised_target_labeling():
    """Verifies target is 1 if min future 14d price <= current_price * 0.95, 0 otherwise."""
    base_time = datetime(2026, 8, 1, tzinfo=timezone.utc)
    # Construct sequence:
    # Day 0: 1000
    # Day 1..10: drops to 900 (900 <= 1000 * 0.95 -> label 1)
    # Day 20..35: stays flat at 900 (future stays 900 -> 900 is NOT <= 900 * 0.95 -> label 0)
    history = []
    for day in range(35):
        dt = base_time + timedelta(days=day)
        if day < 10:
            price = 1000.0 - (day * 10)  # reaches 910
        else:
            price = 900.0
        history.append(
            PriceHistoryPointSchema(
                price=price,
                date=dt.isoformat(),
                availability_status="IN_STOCK",
            )
        )

    cleaned = clean_price_history(history)
    X, y_clf, y_reg, valid_idx = build_supervised_dataset(cleaned, lookahead_days=14, drop_threshold_ratio=0.95)

    assert len(X) > 0
    assert X.shape[1] == len(FEATURE_NAMES)
    # Day 0 drops from 1000 to <= 950 -> label must be 1
    assert y_clf[0] == 1
    # Day 20 stays flat at 900 -> label must be 0
    # Find index corresponding to original day 20
    idx_20 = valid_idx.index(20) if 20 in valid_idx else -1
    if idx_20 >= 0:
        assert y_clf[idx_20] == 0


def test_ml_model_fallback_tier_1_under_14_observations():
    """< 14 observations must trigger Tier 1 baseline historical/moving average model."""
    history = [
        PriceHistoryPointSchema(price=10000.0 - i * 50, date=f"2026-09-{i+1:02d}")
        for i in range(8)
    ]
    pred = price_predictor.predict(history, current_price=9650.0)

    assert pred.model_tier == "TIER_1_RULE_BASED"
    assert pred.model_name == "baseline_moving_average"
    assert 0.0 <= pred.drop_probability <= 1.0
    assert pred.recommended_buy_point is not None


def test_ml_model_fallback_tier_2_14_to_60_observations():
    """14 to 60 observations must trigger Tier 2 Simple ML (Random Forest)."""
    history = [
        PriceHistoryPointSchema(
            price=20000.0 - (i % 6) * 200 + (i * 20),
            date=(datetime(2026, 8, 1, tzinfo=timezone.utc) + timedelta(days=i)).isoformat(),
            availability_status="IN_STOCK",
        )
        for i in range(35)
    ]
    pred = price_predictor.predict(history, current_price=19500.0)

    assert pred.model_tier == "TIER_2_SIMPLE_ML"
    assert pred.model_name == "random_forest"
    assert 0.0 <= pred.drop_probability <= 1.0
    assert pred.sample_count > 0
    assert len(pred.feature_importances) > 0


def test_ml_model_fallback_tier_3_60_plus_observations():
    """60+ observations must trigger Tier 3 rich time-series / XGBoost model."""
    history = [
        PriceHistoryPointSchema(
            price=30000.0 - (i % 10) * 150 - (i * 15),
            date=(datetime(2026, 6, 1, tzinfo=timezone.utc) + timedelta(days=i)).isoformat(),
            availability_status="IN_STOCK",
        )
        for i in range(75)
    ]
    pred = price_predictor.predict(history, current_price=27500.0)

    assert pred.model_tier == "TIER_3_XGBOOST"
    assert pred.model_name == "xgboost"
    assert 0.0 <= pred.drop_probability <= 1.0
    assert pred.predicted_min_price_14d <= 30000.0
    assert len(pred.feature_importances) > 0


# =====================================================================
# 2. Hard BUY Safety Gate Tests
# =====================================================================

def test_hard_buy_safety_gate_passes_healthy_product():
    """BUY is permitted when all 7 safety gates pass."""
    prod = product_service.get_by_id("sony_good_deal")
    assert prod is not None
    result = safety_gate.evaluate(prod)

    assert result.passed is True
    assert result.can_proceed_to_buy() is True
    assert len(result.failed_gates) == 0


def test_hard_buy_safety_gate_blocks_product_mismatch():
    """Gate 1: Exact/Strong Product Match Gate blocks BUY."""
    prod = ProductDetailSchema(
        id="product_mismatch",
        name="Random Unrelated Phone Case Listing",
        current_price=1000.0,
        retailer="Amazon",
        last_checked=datetime.now(timezone.utc).isoformat(),
        price_history=[],
    )
    result = safety_gate.evaluate(prod)

    assert result.passed is False
    assert result.can_proceed_to_buy() is False
    assert "exact_product_match" in result.failed_gates
    assert result.blocked_decision == "CAUTION"


def test_hard_buy_safety_gate_blocks_variant_mismatch():
    """Gate 2: Exact Variant Gate blocks BUY."""
    prod = product_service.get_by_id("variant_mismatch")
    assert prod is not None
    result = safety_gate.evaluate(prod)

    assert result.passed is False
    assert result.can_proceed_to_buy() is False
    assert "exact_variant" in result.failed_gates
    assert result.blocked_decision == "CAUTION"


def test_hard_buy_safety_gate_blocks_stale_data():
    """Gate 3: Fresh Data (< 6h) Gate blocks BUY."""
    prod = product_service.get_by_id("stale_price")
    assert prod is not None
    result = safety_gate.evaluate(prod)

    assert result.passed is False
    assert result.can_proceed_to_buy() is False
    assert "fresh_data" in result.failed_gates
    assert result.blocked_decision == "CAUTION"


def test_hard_buy_safety_gate_blocks_suspicious_seller():
    """Gate 4: Acceptable Seller Gate blocks BUY when rating < 4.0 or RISKY."""
    prod = product_service.get_by_id("laptop_suspicious_seller")
    assert prod is not None
    result = safety_gate.evaluate(prod)

    assert result.passed is False
    assert result.can_proceed_to_buy() is False
    assert "acceptable_seller" in result.failed_gates
    assert result.blocked_decision == "CAUTION"


def test_hard_buy_safety_gate_blocks_out_of_stock():
    """Gate 5: In-stock Availability Gate blocks BUY when out of stock."""
    prod = product_service.get_by_id("out_of_stock")
    assert prod is not None
    result = safety_gate.evaluate(prod)

    assert result.passed is False
    assert result.can_proceed_to_buy() is False
    assert "in_stock_availability" in result.failed_gates
    assert result.blocked_decision == "WAIT"


def test_hard_buy_safety_gate_blocks_untrusted_source():
    """Gate 6: Trusted Source Gate blocks BUY when all sources fail."""
    prod = product_service.get_by_id("all_sources_failed")
    assert prod is not None
    result = safety_gate.evaluate(prod)

    assert result.passed is False
    assert result.can_proceed_to_buy() is False
    assert "trusted_source" in result.failed_gates
    assert result.blocked_decision == "NO_DECISION"


def test_hard_buy_safety_gate_blocks_insufficient_coverage():
    """Gate 7: Sufficient Coverage Gate blocks BUY when product has negligible history."""
    prod = product_service.get_by_id("new_product_no_history")
    assert prod is not None
    result = safety_gate.evaluate(prod)

    assert result.passed is False
    assert result.can_proceed_to_buy() is False
    assert "sufficient_coverage" in result.failed_gates
    assert result.blocked_decision == "NO_DECISION"


def test_ml_cannot_override_blocked_safety_gate():
    """Strictly enforces that ML predictions CANNOT override a blocked safety gate."""
    prod = product_service.get_by_id("laptop_suspicious_seller")
    # Even if we pass it through synthesizer, decision must remain CAUTION and NOT BUY
    dec = decision_synthesizer.synthesize(prod)
    assert dec.decision == "CAUTION"
    assert dec.decision != "BUY"
    assert dec.decision != "GRAB"


# =====================================================================
# 3. Confidence Engine Tests
# =====================================================================

def test_confidence_engine_freshness_categories():
    """Evaluates FRESH (<5m), RECENT (5-30m), STALE (30m-6h), OLD (>6h)."""
    now = datetime.now(timezone.utc)

    # 1. < 5 min -> FRESH
    p_fresh = ProductDetailSchema(
        id="t_fresh",
        name="Fresh Test",
        current_price=1000.0,
        retailer="Amazon",
        last_checked=(now - timedelta(minutes=2)).isoformat(),
        price_history=[],
    )
    r_fresh = confidence_engine.evaluate(p_fresh)
    assert r_fresh.freshness_category == "FRESH"
    assert r_fresh.api_freshness == "FRESH"

    # 2. 5-30 min -> RECENT
    p_recent = ProductDetailSchema(
        id="t_recent",
        name="Recent Test",
        current_price=1000.0,
        retailer="Amazon",
        last_checked=(now - timedelta(minutes=15)).isoformat(),
        price_history=[],
    )
    r_recent = confidence_engine.evaluate(p_recent)
    assert r_recent.freshness_category == "RECENT"
    assert r_recent.api_freshness == "RECENT"

    # 3. 30m-6h -> STALE
    p_stale = ProductDetailSchema(
        id="t_stale",
        name="Stale Test",
        current_price=1000.0,
        retailer="Amazon",
        last_checked=(now - timedelta(hours=3)).isoformat(),
        price_history=[],
    )
    r_stale = confidence_engine.evaluate(p_stale)
    assert r_stale.freshness_category == "STALE"
    assert r_stale.api_freshness == "STALE"

    # 4. > 6h -> OLD
    p_old = ProductDetailSchema(
        id="t_old",
        name="Old Test",
        current_price=1000.0,
        retailer="Amazon",
        last_checked=(now - timedelta(hours=12)).isoformat(),
        price_history=[],
    )
    r_old = confidence_engine.evaluate(p_old)
    assert r_old.freshness_category == "OLD"
    assert r_old.confidence_level == "LOW"


def test_confidence_engine_confidence_levels():
    """Tests HIGH, MEDIUM, LOW confidence assignments."""
    sony = product_service.get_by_id("sony_good_deal")
    r_sony = confidence_engine.evaluate(sony)
    assert r_sony.confidence_level == "HIGH"

    suspicious = product_service.get_by_id("laptop_suspicious_seller")
    r_suspicious = confidence_engine.evaluate(suspicious)
    assert r_suspicious.confidence_level == "MEDIUM"

    all_failed = product_service.get_by_id("all_sources_failed")
    r_all_failed = confidence_engine.evaluate(all_failed)
    assert r_all_failed.confidence_level == "LOW"


# =====================================================================
# 4. Structured Decision Synthesizer & API Contract Verification
# =====================================================================

def test_decision_synthesizer_exact_contract_json():
    """Verifies synthesis returns exact schema and all 11 required contract fields."""
    prod = product_service.get_by_id("sony_good_deal")
    dec = decision_synthesizer.synthesize(prod)

    d_dict = dec.model_dump()
    required_keys = {
        "decision",
        "confidence_level",
        "primary_reason",
        "secondary_reasons",
        "buy_point",
        "best_offer_id",
        "data_freshness",
        "data_coverage",
        "checked_at",
        "model_version",
        "decision_rules_version",
    }
    assert required_keys.issubset(set(d_dict.keys()))
    assert dec.model_version == "shopq-decision-v2.1"
    assert dec.decision_rules_version == "rules-2026.10"
    assert dec.decision == "BUY"
    assert dec.confidence_level == "HIGH"
    assert dec.data_freshness == "FRESH"
    assert dec.data_coverage == "98%"
    assert dec.buy_point == prod.buy_point


def test_all_12_catalog_scenarios_synthesize_correctly():
    """Tests that all 12 core catalog scenarios produce valid, compliant decisions."""
    expected_decisions = {
        "sony_good_deal": "BUY",
        "iphone_wait": "WAIT",
        "laptop_suspicious_seller": "CAUTION",
        "variant_mismatch": "CAUTION",
        "stale_price": "CAUTION",
        "out_of_stock": "WAIT",
        "new_product_no_history": "NO_DECISION",
        "all_sources_failed": "NO_DECISION",
        "seller_changed": "CAUTION",
        "nike_better_alternative": "CHECK_ALT",
        "samsung_s24": "WAIT_SALE",
        "oneplus_12": "DONT_RUSH",
    }

    for prod_id, exp_decision in expected_decisions.items():
        prod = product_service.get_by_id(prod_id)
        assert prod is not None, f"Product {prod_id} not found in catalog!"
        decision = decision_service.evaluate_decision(prod)

        assert decision.decision == exp_decision, (
            f"Expected {exp_decision} for {prod_id}, got {decision.decision}"
        )
        assert decision.confidence_level in ("HIGH", "MEDIUM", "LOW")
        assert decision.data_freshness in ("FRESH", "RECENT", "STALE")
        assert "%" in decision.data_coverage
        assert decision.model_version == "shopq-decision-v2.1"
        assert decision.decision_rules_version == "rules-2026.10"


def test_decision_service_analyze_product_integration():
    """Tests decision_service.analyze_product returns complete ProductAnalysisResponse."""
    resp = decision_service.analyze_product("sony_good_deal")
    assert resp.product.id == "sony_good_deal"
    assert resp.decision.decision == "BUY"
    assert resp.decision.confidence_level == "HIGH"
    assert resp.decision.model_version == "shopq-decision-v2.1"
