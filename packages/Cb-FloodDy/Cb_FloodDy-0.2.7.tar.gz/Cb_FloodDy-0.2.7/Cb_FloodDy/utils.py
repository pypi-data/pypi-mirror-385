"""
Utility functions for Cb_FloodDy
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Tuple, Optional

import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

__all__ = [
    "set_global_seeds",
    "ensure_dir",
    "MinMaxPair",
    "fit_minmax",
    "transform_minmax",
    "inverse_transform_minmax",
    "build_sequences",
    "nse",
    "kge",
    "willmott_d",
    "mbias",
    "rmse",
    "mae",
    "ts_scatter_plot",
]

def set_global_seeds(seed: int = 42):
    import random, numpy as _np
    try:
        import tensorflow as tf
        tf.random.set_seed(seed)
    except Exception:
        pass
    random.seed(seed)
    _np.random.seed(seed)

def ensure_dir(path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

@dataclass
class MinMaxPair:
    x_scaler: MinMaxScaler
    y_scaler: MinMaxScaler

def fit_minmax(X: np.ndarray, y: np.ndarray) -> MinMaxPair:
    x_scaler = MinMaxScaler(feature_range=(0, 1))
    X2 = X.reshape(-1, X.shape[-1]) if X.ndim == 3 else X
    x_scaler.fit(X2)
    y_scaler = MinMaxScaler(feature_range=(0, 1))
    y_scaler.fit(y.reshape(-1, 1))
    return MinMaxPair(x_scaler, y_scaler)

def transform_minmax(X: np.ndarray, y: Optional[np.ndarray], scalers: MinMaxPair):
    X2 = X.reshape(-1, X.shape[-1]) if X.ndim == 3 else X
    Xt = scalers.x_scaler.transform(X2)
    Xt = Xt.reshape(X.shape) if X.ndim == 3 else Xt
    if y is None:
        return Xt, None
    yt = scalers.y_scaler.transform(y.reshape(-1, 1)).reshape(-1)
    return Xt, yt

def inverse_transform_minmax(yhat: np.ndarray, scalers: MinMaxPair):
    return scalers.y_scaler.inverse_transform(yhat.reshape(-1, 1)).reshape(-1)

def build_sequences(X: np.ndarray, y: np.ndarray, lookback: int, horizon: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    assert X.shape[0] == y.shape[0], "X and y must have equal length"
    n = X.shape[0] - lookback - horizon + 1
    Xs = np.stack([X[i:i+lookback] for i in range(n)], axis=0)
    ys = y[lookback + horizon - 1 : lookback + horizon - 1 + n]
    return Xs, ys

def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    return float(np.sqrt(np.mean((y_pred - y_true) ** 2)))

def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    return float(np.mean(np.abs(y_pred - y_true)))

def nse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    denom = np.sum((y_true - np.mean(y_true)) ** 2)
    if denom == 0:
        return float("nan")
    return 1.0 - float(np.sum((y_true - y_pred) ** 2) / denom)

def kge(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    r = np.corrcoef(y_true, y_pred)[0, 1] if len(y_true) > 1 else np.nan
    alpha = np.std(y_pred) / (np.std(y_true) + 1e-12)
    beta = np.mean(y_pred) / (np.mean(y_true) + 1e-12)
    return 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)

def willmott_d(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    num = np.sum((y_pred - y_true) ** 2)
    den = np.sum((np.abs(y_pred - np.mean(y_true)) + np.abs(y_true - np.mean(y_true))) ** 2)
    if den == 0:
        return float("nan")
    return 1.0 - float(num / den)

def mbias(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    return float((np.mean(y_pred) - np.mean(y_true)) / (np.mean(y_true) + 1e-12))

def ts_scatter_plot(y_true, y_pred, out_path: str, title: str = "Prediction vs Observations"):
    ensure_dir(out_path)
    y_true = np.asarray(y_true).reshape(-1)
    y_pred = np.asarray(y_pred).reshape(-1)
    import numpy as np
    # Time series
    plt.figure(figsize=(10, 3.2))
    plt.plot(y_true, label="Obs")
    plt.plot(y_pred, label="Pred", alpha=0.8)
    plt.legend(); plt.title(title + " — Time Series"); plt.tight_layout()
    plt.savefig(out_path.replace(".png", "_ts.png")); plt.close()
    # 1:1 scatter
    lims = [min(np.min(y_true), np.min(y_pred)), max(np.max(y_true), np.max(y_pred))]
    plt.figure(figsize=(4.5, 4.5))
    plt.scatter(y_true, y_pred, s=10, alpha=0.7)
    plt.plot(lims, lims)
    plt.xlabel("Obs"); plt.ylabel("Pred"); plt.title(title + " — 1:1")
    plt.tight_layout(); plt.savefig(out_path.replace(".png", "_scatter.png")); plt.close()
