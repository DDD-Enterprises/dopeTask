"""UI package surfaces.

This package re-exports the legacy neon helpers from ``dopetask._ui_legacy``
so existing imports continue to work while package submodules are added.

The legacy module used to live at ``dopetask/ui.py`` and was loaded via
``importlib.util.spec_from_file_location`` because a module and a package
cannot share the ``dopetask.ui`` name; that made every re-exported name
invisible to static type checkers. Renaming the legacy module to
``dopetask._ui_legacy`` lets this be a normal, statically analyzable import.
"""

from __future__ import annotations

from dopetask._ui_legacy import *  # noqa: F401,F403

__all__ = [name for name in dir() if not name.startswith("_")]
