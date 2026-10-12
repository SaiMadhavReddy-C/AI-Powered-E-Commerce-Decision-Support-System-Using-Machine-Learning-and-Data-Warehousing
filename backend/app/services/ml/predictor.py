"""High-level ML predictor executing model selection and fallback based on data availability:
- < 14 observations -> Tier 1 Baseline moving average
- 14–60 observations -> Tier 2 Simple ML (Random Forest / Linear Regression)
- 60+ observations -> Tier 3 XGBoost Time-Series Model
"""

from typing import List, Optional
import numpy as np

from app.schemas.product import PriceHistoryPointSchema
from app.services.ml.data_prep import (
    clean_price_history,
    build_supervised_dataset,
    extract_features_at_step,
    CleanedPricePoint,
)
from app.services.ml.models import (
    PricePredictionResult,
    BaselineMovingAverageModel,
    SimpleMLModel,
    XGBoostTimeSeriesModel,
)
from app.core.logging import logger


class PricePredictor:
    """Orchestrates ML feature pipeline, model selection, and fallback execution."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.baseline_model = BaselineMovingAverageModel()
        self.simple_ml_model = SimpleMLModel(random_state=random_state)
        self.xgboost_model = XGBoostTimeSeriesModel(random_state=random_state)

    def predict(
        self,
        price_history: List[PriceHistoryPointSchema],
        current_price: float,
    ) -> PricePredictionResult:
        """
        Executes model fallback strategy based on price history observation count.
        """
        cleaned_points: List[CleanedPricePoint] = clean_price_history(price_history)
        n_obs = len(cleaned_points)

        # Fallback 1: < 14 observations -> Rule-based baseline
        if n_obs < 14:
            return self.baseline_model.predict(cleaned_points, current_price)

        # Prepare supervised dataset for ML models
        X, y_clf, y_reg, valid_indices = build_supervised_dataset(
            cleaned_points,
            lookahead_days=14,
            drop_threshold_ratio=0.95,
        )

        n_samples = len(X)
        if n_samples < 7:
            # Not enough valid historical lookahead pairs; fall back to baseline
            return self.baseline_model.predict(cleaned_points, current_price)

        # Extract features for current market state (latest observation)
        prices = [p.price for p in cleaned_points]
        timestamps = [p.timestamp for p in cleaned_points]
        current_features = extract_features_at_step(prices, len(prices) - 1, timestamps)

        # Fallback 2: 60+ observations -> Tier 3 XGBoost
        if n_obs >= 60 and n_samples >= 20:
            try:
                return self.xgboost_model.train_and_predict(
                    X=X,
                    y_clf=y_clf,
                    y_reg=y_reg,
                    current_features=current_features,
                    current_price=current_price,
                    cleaned_points=cleaned_points,
                )
            except Exception as e:
                logger.warning(f"XGBoost training encountered error: {e}. Falling back to Simple ML.")

        # Fallback 3: 14–60 observations (or XGBoost fallback) -> Tier 2 Simple ML (Random Forest)
        try:
            return self.simple_ml_model.train_and_predict(
                X=X,
                y_clf=y_clf,
                y_reg=y_reg,
                current_features=current_features,
                current_price=current_price,
                cleaned_points=cleaned_points,
            )
        except Exception as e:
            logger.warning(f"Simple ML training encountered error: {e}. Falling back to Baseline.")
            return self.baseline_model.predict(cleaned_points, current_price)


price_predictor = PricePredictor()
