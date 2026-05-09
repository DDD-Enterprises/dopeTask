"""UI package surfaces.

This package re-exports the legacy neon helpers from ``src/dopetask/ui.py`` so
existing imports continue to work while package submodules are added.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_legacy_ui_module() -> ModuleType:
    legacy_path = Path(__file__).resolve().parents[1] / "ui.py"
    spec = importlib.util.spec_from_file_location("dopetask._legacy_ui", legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy UI module from {legacy_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_legacy_ui = _load_legacy_ui_module()
__all__: list[str] = []

for _name in dir(_legacy_ui):
    if _name.startswith("_"):
        continue
    globals()[_name] = getattr(_legacy_ui, _name)
    __all__.append(_name)

__all__.sort()
