"""
Cb_FloodDy package root (lazy heavy modules).
"""
from . import voronoi_clusters

__all__ = [
    "voronoi_clusters",
    "model_training",
    "model_prediction",
    "bayesian_opt_tuning",
]

def __getattr__(name):
    if name == "model_training":
        from . import model_training as _mt
        return _mt
    if name == "model_prediction":
        from . import model_prediction as _mp
        return _mp
    if name == "bayesian_opt_tuning":
        from . import bayesian_opt_tuning as _bo
        return _bo
    raise AttributeError(f"module 'Cb_FloodDy' has no attribute {name!r}")
