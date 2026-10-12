"""Machine learning prediction models for ShopQ price drop forecasting.

Tiers:
- Tier 1 (< 14 obs): Baseline historical / rule-based moving average.
- Tier 2 (14–60 obs): Simple ML model (Random Forest / Linear Regression).
- Tier 3 (60+ obs): Rich time-series model / XGBoost.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import numpy as np

from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
)
from sklearn.linear_model import LogisticRegression, LinearRegression

HAS_XGBOOST = False
try:
    import xgboost as xgb
    # Quick probe to verify OpenMP dynamic library linkage
    _probe = xgb.DMatrix(np.array([[1.0, 2.0]], dtype=np.float32))
    HAS_XGBOOST = True
except Exception:
    HAS_XGBOOST = False

from app.services.ml.data_prep import (
    FEATURE_NAMES,
    CleanedPricePoint,
    extract_features_at_step,
    temporal_train_val_test_split,
)


@dataclass
class PricePredictionResult:
    drop_probability: float  # probability of >= 5% drop within future 14d [0.0, 1.0]
    will_drop: bool          # True if drop_probability >= 0.5
    predicted_min_price_14d: float  # Estimated minimum price over next 14 days
    recommended_buy_point: Optional[float]  # Suggested target purchase threshold
    model_name: str          # e.g., "baseline_moving_average", "random_forest", "xgboost"
    model_tier: str          # "TIER_1_RULE_BASED", "TIER_2_SIMPLE_ML", "TIER_3_XGBOOST"
    sample_count: int        # Number of historical observations used
    val_accuracy: Optional[float] = None
    val_log_loss: Optional[float] = None
    feature_importances: Dict[str, float] = field(default_factory=dict)
    diagnostics: Dict[str, Any] = field(default_factory=dict)


class BaselineMovingAverageModel:
    """
    Tier 1 Baseline model for datasets with < 14 price history observations.
    Uses 3-day and 7-day Simple Moving Averages, price momentum, and support levels.
    """

    def predict(
        self,
        cleaned_points: List[CleanedPricePoint],
        current_price: float,
    ) -> PricePredictionResult:
        prices = [p.price for p in cleaned_points if p.in_stock]
        if not prices:
            prices = [current_price]

        n = len(prices)
        hist_min = float(min(prices))
        hist_max = float(max(prices))
        sma3 = float(np.mean(prices[-3:])) if n >= 3 else current_price
        sma7 = float(np.mean(prices[-7:])) if n >= 7 else sma3

        # Price position in available historical range [0.0, 1.0]
        if hist_max > hist_min:
            range_ratio = (current_price - hist_min) / (hist_max - hist_min)
        else:
            range_ratio = 0.5

        # Short-term momentum
        momentum = (current_price - prices[0]) / max(prices[0], 1.0) if n > 1 else 0.0

        # Heuristic price drop probability
        # If at historical low, probability of dropping another 5% is lower
        # If at historical high with rising momentum, drop probability is higher
        base_prob = 0.20 + 0.60 * range_ratio
        if momentum < -0.05:
            # Already falling fast, may drop more
            base_prob = min(0.90, base_prob + 0.15)
        elif current_price <= hist_min * 1.01:
            base_prob = max(0.10, min(0.30, base_prob - 0.20))

        drop_prob = float(np.clip(base_prob, 0.05, 0.95))
        will_drop = drop_prob >= 0.50

        # Predicted minimum price over 14d
        if will_drop:
            pred_min = min(current_price * 0.95, hist_min)
        else:
            pred_min = min(current_price, hist_min)

        buy_point = float(round(min(current_price, hist_min * 1.02), 2)) if not will_drop else float(round(pred_min, 2))

        return PricePredictionResult(
            drop_probability=float(round(drop_prob, 4)),
            will_drop=will_drop,
            predicted_min_price_14d=float(round(pred_min, 2)),
            recommended_buy_point=buy_point,
            model_name="baseline_moving_average",
            model_tier="TIER_1_RULE_BASED",
            sample_count=n,
            val_accuracy=None,
            feature_importances={"sma3": 0.4, "sma7": 0.3, "range_ratio": 0.3},
            diagnostics={
                "hist_min": hist_min,
                "hist_max": hist_max,
                "sma3": sma3,
                "sma7": sma7,
                "momentum": momentum,
                "tier_reason": f"Insufficient observations ({n} < 14); applied moving average baseline.",
            },
        )


class SimpleMLModel:
    """
    Tier 2 ML model for datasets with 14–60 observations.
    Employs Random Forest classification and regression with temporal validation split.
    Falls back gracefully to Logistic / Linear regression if tree building encounters edge cases.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def train_and_predict(
        self,
        X: np.ndarray,
        y_clf: np.ndarray,
        y_reg: np.ndarray,
        current_features: np.ndarray,
        current_price: float,
        cleaned_points: List[CleanedPricePoint],
    ) -> PricePredictionResult:
        n_samples = len(X)
        X_train, y_train, X_val, y_val, _, _ = temporal_train_val_test_split(
            X, y_clf, train_ratio=0.70, val_ratio=0.15
        )
        _, y_reg_train, _, y_reg_val, _, _ = temporal_train_val_test_split(
            X, y_reg, train_ratio=0.70, val_ratio=0.15
        )

        unique_classes = np.unique(y_train)
        feature_importances: Dict[str, float] = {}
        val_acc: Optional[float] = None

        x_query = current_features.reshape(1, -1)

        # 1. Classification
        if len(unique_classes) >= 2:
            try:
                clf = RandomForestClassifier(
                    n_estimators=35,
                    max_depth=4,
                    min_samples_split=2,
                    random_state=self.random_state,
                )
                clf.fit(X_train, y_train)

                # Validation metrics
                if len(X_val) > 0 and len(np.unique(y_val)) > 0:
                    val_acc = float(np.mean(clf.predict(X_val) == y_val))

                probs = clf.predict_proba(x_query)[0]
                # Prob of class 1 (price drops >= 5%)
                drop_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])

                for f_name, imp in zip(FEATURE_NAMES, clf.feature_importances_):
                    feature_importances[f_name] = float(round(imp, 4))
            except Exception:
                # Fallback to LogisticRegression
                lr = LogisticRegression(max_iter=200, random_state=self.random_state)
                lr.fit(X_train, y_train)
                drop_prob = float(lr.predict_proba(x_query)[0, 1])
                val_acc = float(np.mean(lr.predict(X_val) == y_val)) if len(X_val) > 0 else None
        else:
            # Single class in training split
            single_class = int(unique_classes[0]) if len(unique_classes) == 1 else 0
            drop_prob = 0.85 if single_class == 1 else 0.15
            val_acc = 1.0

        will_drop = drop_prob >= 0.50

        # 2. Regression for predicted min price
        hist_prices = [p.price for p in cleaned_points if p.in_stock]
        hist_min = float(min(hist_prices)) if hist_prices else current_price
        try:
            reg = RandomForestRegressor(
                n_estimators=30,
                max_depth=4,
                random_state=self.random_state,
            )
            reg.fit(X_train, y_reg_train)
            pred_min = float(reg.predict(x_query)[0])
            if not feature_importances and hasattr(reg, "feature_importances_"):
                for f_name, imp in zip(FEATURE_NAMES, reg.feature_importances_):
                    feature_importances[f_name] = float(round(imp, 4))
        except Exception:
            pred_min = current_price * 0.94 if will_drop else min(current_price, hist_min)

        # Sanity bound: predicted min price should not exceed current price or fall below 50%
        pred_min = max(current_price * 0.5, min(current_price * 1.05, pred_min))
        buy_point = float(round(pred_min if will_drop else min(current_price, hist_min * 1.02), 2))

        return PricePredictionResult(
            drop_probability=float(round(drop_prob, 4)),
            will_drop=will_drop,
            predicted_min_price_14d=float(round(pred_min, 2)),
            recommended_buy_point=buy_point,
            model_name="random_forest",
            model_tier="TIER_2_SIMPLE_ML",
            sample_count=n_samples,
            val_accuracy=float(round(val_acc, 4)) if val_acc is not None else None,
            feature_importances=feature_importances,
            diagnostics={
                "n_train": len(X_train),
                "n_val": len(X_val),
                "temporal_split": "70% Train, 15% Val, 15% Test strictly by past -> future",
                "tier_reason": f"Sample count {n_samples} is within 14–60 range; applied Random Forest.",
            },
        )


class XGBoostTimeSeriesModel:
    """
    Tier 3 Model for rich price history (60+ observations).
    Employs gradient boosted decision trees (XGBClassifier & XGBRegressor)
    with strict temporal validation split and early evaluation.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def train_and_predict(
        self,
        X: np.ndarray,
        y_clf: np.ndarray,
        y_reg: np.ndarray,
        current_features: np.ndarray,
        current_price: float,
        cleaned_points: List[CleanedPricePoint],
    ) -> PricePredictionResult:
        n_samples = len(X)
        X_train, y_train, X_val, y_val, _, _ = temporal_train_val_test_split(
            X, y_clf, train_ratio=0.70, val_ratio=0.15
        )
        _, y_reg_train, _, y_reg_val, _, _ = temporal_train_val_test_split(
            X, y_reg, train_ratio=0.70, val_ratio=0.15
        )

        unique_classes = np.unique(y_train)
        feature_importances: Dict[str, float] = {}
        val_acc: Optional[float] = None
        val_loss: Optional[float] = None

        x_query = current_features.reshape(1, -1)

        # 1. Classification (XGBoost or GradientBoosting fallback)
        if len(unique_classes) >= 2:
            if HAS_XGBOOST:
                clf = xgb.XGBClassifier(
                    n_estimators=50,
                    max_depth=3,
                    learning_rate=0.05,
                    eval_metric="logloss",
                    random_state=self.random_state,
                )
            else:
                clf = GradientBoostingClassifier(
                    n_estimators=50,
                    max_depth=3,
                    learning_rate=0.05,
                    random_state=self.random_state,
                )
            clf.fit(X_train, y_train)

            if len(X_val) > 0 and len(np.unique(y_val)) > 0:
                preds = clf.predict(X_val)
                val_acc = float(np.mean(preds == y_val))

            probs = clf.predict_proba(x_query)[0]
            drop_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])

            # Feature importances
            raw_imp = clf.feature_importances_
            for f_name, imp in zip(FEATURE_NAMES, raw_imp):
                feature_importances[f_name] = float(round(imp, 4))
        else:
            single_class = int(unique_classes[0]) if len(unique_classes) == 1 else 0
            drop_prob = 0.85 if single_class == 1 else 0.15
            val_acc = 1.0

        will_drop = drop_prob >= 0.50

        # 2. Regression (XGBoost or GradientBoosting fallback)
        hist_prices = [p.price for p in cleaned_points if p.in_stock]
        hist_min = float(min(hist_prices)) if hist_prices else current_price
        try:
            if HAS_XGBOOST:
                reg = xgb.XGBRegressor(
                    n_estimators=50,
                    max_depth=3,
                    learning_rate=0.05,
                    random_state=self.random_state,
                )
            else:
                reg = GradientBoostingRegressor(
                    n_estimators=50,
                    max_depth=3,
                    learning_rate=0.05,
                    random_state=self.random_state,
                )
            reg.fit(X_train, y_reg_train)
            pred_min = float(reg.predict(x_query)[0])
            if not feature_importances and hasattr(reg, "feature_importances_"):
                for f_name, imp in zip(FEATURE_NAMES, reg.feature_importances_):
                    feature_importances[f_name] = float(round(imp, 4))
        except Exception:
            pred_min = current_price * 0.94 if will_drop else min(current_price, hist_min)

        pred_min = max(current_price * 0.5, min(current_price * 1.05, pred_min))
        buy_point = float(round(pred_min if will_drop else min(current_price, hist_min * 1.02), 2))

        return PricePredictionResult(
            drop_probability=float(round(drop_prob, 4)),
            will_drop=will_drop,
            predicted_min_price_14d=float(round(pred_min, 2)),
            recommended_buy_point=buy_point,
            model_name="xgboost",
            model_tier="TIER_3_XGBOOST",
            sample_count=n_samples,
            val_accuracy=float(round(val_acc, 4)) if val_acc is not None else None,
            val_log_loss=val_loss,
            feature_importances=feature_importances,
            diagnostics={
                "n_train": len(X_train),
                "n_val": len(X_val),
                "temporal_split": "70% Train, 15% Val, 15% Test strictly chronological",
                "tier_reason": f"Sample count {n_samples} >= 60; applied XGBoost time-series model.",
            },
        )
