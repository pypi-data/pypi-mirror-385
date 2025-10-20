"""CLI entrypoints for Cb_FloodDy"""
import sys

def _call_main(module_name: str) -> int:
    try:
        module = __import__(f"Cb_FloodDy.{module_name}", fromlist=["main"])
        if hasattr(module, "main"):
            return int(module.main() or 0)
        raise AttributeError(f"Module {module_name!r} has no callable main()")
    except Exception as e:
        print(f"[Cb_FloodDy] Error: {e}", file=sys.stderr)
        return 1

def train():
    sys.exit(_call_main("model_training"))

def predict():
    sys.exit(_call_main("model_prediction"))

def tune():
    sys.exit(_call_main("bayesian_opt_tuning"))
