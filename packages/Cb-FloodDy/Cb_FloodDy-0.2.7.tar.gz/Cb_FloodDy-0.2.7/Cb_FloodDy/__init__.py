"""
Cb_FloodDy package root (lazy heavy modules).
"""

from . import voronoi_clusters  # eager: light and frequently used

__all__ = [
    "voronoi_clusters",
    "model_training",
    "model_prediction",
    "bayesian_opt_tuning",
]

def __getattr__(name):
    # Lazy-load heavier submodules only when requested
    if name in {"model_training", "model_prediction", "bayesian_opt_tuning"}:
        import importlib
        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(f"module 'Cb_FloodDy' has no attribute {name!r}")
