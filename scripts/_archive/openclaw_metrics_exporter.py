"""
openclaw_metrics_exporter.py — importable alias for openclaw-metrics-exporter.py

Python cannot import modules with hyphens in their filename. This wrapper uses
importlib to load the hyphenated source file and re-exports everything.
"""
import importlib.util
import sys
from pathlib import Path

_src = Path(__file__).parent / "openclaw-metrics-exporter.py"
_spec = importlib.util.spec_from_file_location("openclaw_metrics_exporter_impl", _src)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

# Re-export every public name
globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("__")})
