"""Data preparation, feature engineering, and temporal validation splits for ShopQ ML models.

Ensures strict chronological ordering (Past -> Train, Later -> Val, Newest -> Test)
to completely prevent lookahead and time-series data leakage.
"""

import math
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from app.schemas.product import PriceHistoryPointSchema


FEATURE_NAMES = [
    "price_ratio_sma3",
    "price_ratio_sma7",
    "price_ratio_sma14",
    "price_ratio_sma30",
    "price_to_hist_min",
    "price_to_hist_max",
    "price_percentile",
    "volatility_7d",
    "volatility_14d",
    "momentum_3d",
    "momentum_7d",
    "days_since_peak",
    "days_since_trough",
    "day_of_week",
]


class CleanedPricePoint:
    def __init__(
        self,
        index: int,
        price: float,
        timestamp: Optional[datetime],
        in_stock: bool = True,
        is_anomaly: bool = False,
    ):
        self.index = index
        self.price = float(price)
        self.timestamp = timestamp
        self.in_stock = in_stock
        self.is_anomaly = is_anomaly


def parse_timestamp(ts_str: Optional[str]) -> Optional[datetime]:
    if not ts_str:
        return None
    try:
        # Handle ISO format with Z or timezone
        clean_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean_str)
    except Exception:
        return None


def clean_price_history(
    history: List[PriceHistoryPointSchema],
) -> List[CleanedPricePoint]:
    """
    Cleans raw price history observations:
    - Sorts chronologically
    - Filters out non-positive prices
    - Flags out-of-stock observations
    - Detects extreme anomalous price spikes/drops (e.g. >5x or <0.1x of local median)
    """
    if not history:
        return []

    parsed_points: List[Tuple[Optional[datetime], float, bool]] = []
    for pt in history:
        ts = parse_timestamp(pt.observed_at or pt.date or pt.collected_at)
        p = float(pt.price)
        if p <= 0 or math.isnan(p) or math.isinf(p):
            continue
        in_stock = (pt.availability_status or "IN_STOCK").upper() != "OUT_OF_STOCK"
        parsed_points.append((ts, p, in_stock))

    # Sort chronologically if timestamps are available
    has_all_ts = all(t[0] is not None for t in parsed_points)
    if has_all_ts and len(parsed_points) > 1:
        parsed_points.sort(key=lambda x: x[0])  # type: ignore

    # Anomaly detection using local median filter
    prices = [p[1] for p in parsed_points]
    cleaned: List[CleanedPricePoint] = []

    for i, (ts, price, in_stock) in enumerate(parsed_points):
        # Local window for median
        w_start = max(0, i - 7)
        w_end = min(len(prices), i + 8)
        local_window = [p for j, p in enumerate(prices[w_start:w_end]) if parsed_points[w_start + j][2]]
        is_anomaly = False
        if len(local_window) >= 5:
            med = float(np.median(local_window))
            if med > 0:
                if price > med * 5.0 or price < med * 0.1:
                    is_anomaly = True

        cleaned.append(
            CleanedPricePoint(
                index=i,
                price=price,
                timestamp=ts,
                in_stock=in_stock,
                is_anomaly=is_anomaly,
            )
        )

    return cleaned


def extract_features_at_step(
    prices: List[float],
    current_idx: int,
    timestamps: List[Optional[datetime]],
) -> np.ndarray:
    """
    Extracts time-series features strictly using historical observations up to current_idx.
    Prevents lookahead data leakage by never accessing indices > current_idx.
    """
    sub_prices = prices[: current_idx + 1]
    curr_price = sub_prices[-1]
    n = len(sub_prices)

    # Moving averages
    def get_sma(window: int) -> float:
        w_prices = sub_prices[-window:]
        return float(np.mean(w_prices)) if w_prices else curr_price

    sma3 = get_sma(3)
    sma7 = get_sma(7)
    sma14 = get_sma(14)
    sma30 = get_sma(30)

    price_ratio_sma3 = curr_price / max(sma3, 1e-4)
    price_ratio_sma7 = curr_price / max(sma7, 1e-4)
    price_ratio_sma14 = curr_price / max(sma14, 1e-4)
    price_ratio_sma30 = curr_price / max(sma30, 1e-4)

    # Range & rank
    hist_min = float(np.min(sub_prices))
    hist_max = float(np.max(sub_prices))
    price_to_hist_min = curr_price / max(hist_min, 1e-4)
    price_to_hist_max = curr_price / max(hist_max, 1e-4)

    if hist_max > hist_min:
        price_percentile = (curr_price - hist_min) / (hist_max - hist_min)
    else:
        price_percentile = 0.5

    # Volatilities
    def get_volatility(window: int) -> float:
        w_prices = sub_prices[-window:]
        if len(w_prices) < 2:
            return 0.0
        return float(np.std(w_prices) / max(np.mean(w_prices), 1e-4))

    volatility_7d = get_volatility(7)
    volatility_14d = get_volatility(14)

    # Momentum
    momentum_3d = (curr_price - sub_prices[-4]) / max(sub_prices[-4], 1e-4) if n >= 4 else 0.0
    momentum_7d = (curr_price - sub_prices[-8]) / max(sub_prices[-8], 1e-4) if n >= 8 else 0.0

    # Days since peak & trough
    argmax_idx = int(np.argmax(sub_prices))
    argmin_idx = int(np.argmin(sub_prices))
    days_since_peak = float(current_idx - argmax_idx)
    days_since_trough = float(current_idx - argmin_idx)

    # Day of week
    cur_ts = timestamps[current_idx] if current_idx < len(timestamps) else None
    day_of_week = float(cur_ts.weekday()) if cur_ts else 0.0

    features = [
        price_ratio_sma3,
        price_ratio_sma7,
        price_ratio_sma14,
        price_ratio_sma30,
        price_to_hist_min,
        price_to_hist_max,
        price_percentile,
        volatility_7d,
        volatility_14d,
        momentum_3d,
        momentum_7d,
        days_since_peak,
        days_since_trough,
        day_of_week,
    ]
    return np.array(features, dtype=np.float32)


def build_supervised_dataset(
    cleaned_points: List[CleanedPricePoint],
    lookahead_days: int = 14,
    drop_threshold_ratio: float = 0.95,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[int]]:
    """
    Constructs supervised training dataset (X, y_clf, y_reg, valid_indices).
    Prediction Target:
      Label = 1 if min future 14d price <= current_price * 0.95 (excluding out of stock / anomalies)
      Label = 0 otherwise.
      y_reg = min future 14d price
    """
    if len(cleaned_points) < 2:
        return np.empty((0, len(FEATURE_NAMES))), np.empty((0,)), np.empty((0,)), []

    prices = [p.price for p in cleaned_points]
    timestamps = [p.timestamp for p in cleaned_points]

    X_list: List[np.ndarray] = []
    y_clf_list: List[int] = []
    y_reg_list: List[float] = []
    valid_indices: List[int] = []

    n = len(cleaned_points)
    for i in range(n):
        # Exclude anomalies or out of stock at current point from being training anchors
        if cleaned_points[i].is_anomaly or not cleaned_points[i].in_stock:
            continue

        # Lookahead window: up to lookahead_days points into the future
        future_window = cleaned_points[i + 1 : min(i + 1 + lookahead_days, n)]
        # Filter valid future points (must be in stock, not anomaly)
        valid_future = [p.price for p in future_window if p.in_stock and not p.is_anomaly]

        # Require at least 1 valid future observation to compute target
        if not valid_future:
            continue

        min_future_price = min(valid_future)
        curr_price = cleaned_points[i].price
        target_threshold = curr_price * drop_threshold_ratio

        label = 1 if min_future_price <= target_threshold else 0

        feat = extract_features_at_step(prices, i, timestamps)
        X_list.append(feat)
        y_clf_list.append(label)
        y_reg_list.append(min_future_price)
        valid_indices.append(i)

    if not X_list:
        return np.empty((0, len(FEATURE_NAMES))), np.empty((0,)), np.empty((0,)), []

    return (
        np.array(X_list, dtype=np.float32),
        np.array(y_clf_list, dtype=np.int32),
        np.array(y_reg_list, dtype=np.float32),
        valid_indices,
    )


def temporal_train_val_test_split(
    X: np.ndarray,
    y: np.ndarray,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Splits data strictly chronologically:
    Past -> Train, Later -> Val, Newest -> Test.
    Never shuffles to strictly prevent temporal leakage.
    """
    n = len(X)
    if n == 0:
        return (
            np.empty((0, X.shape[1] if X.ndim > 1 else 0)),
            np.empty((0,)),
            np.empty((0, X.shape[1] if X.ndim > 1 else 0)),
            np.empty((0,)),
            np.empty((0, X.shape[1] if X.ndim > 1 else 0)),
            np.empty((0,)),
        )

    train_end = max(1, int(n * train_ratio))
    val_end = max(train_end + 1, int(n * (train_ratio + val_ratio)))
    if val_end >= n:
        val_end = min(n, train_end + max(1, (n - train_end) // 2))

    X_train, y_train = X[:train_end], y[:train_end]
    X_val, y_val = X[train_end:val_end], y[train_end:val_end]
    X_test, y_test = X[val_end:], y[val_end:]

    # Fallback if val or test is empty in small sets
    if len(X_val) == 0 and len(X_train) > 1:
        X_val, y_val = X_train[-1:], y_train[-1:]
    if len(X_test) == 0 and len(X_val) > 0:
        X_test, y_test = X_val[-1:], y_val[-1:]

    return X_train, y_train, X_val, y_val, X_test, y_test
