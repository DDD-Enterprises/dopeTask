"""Read-only Asset Library cockpit placeholder."""

from __future__ import annotations

from typing import Any

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from dopetask.ui.widgets.banners import asset_banner


ASSET_PLACEHOLDER = (
    "Asset listing/preview is not implemented in this read-only cockpit slice. "
    "dope-agent-system remains Asset / Template Plane only."
)


def render_asset_library(
    status_payload: dict[str, Any],
    series_id: str | None = None,
    tp_id: str | None = None,
) -> Group:
    del series_id, tp_id
    table = Table(title="Asset Library")
    table.add_column("field")
    table.add_column("value")
    table.add_row("DAS configured", _text(status_payload.get("das_configured")))
    table.add_row("DAS path", _text(status_payload.get("das_path")))
    table.add_row("version drift", _text(status_payload.get("version_drift")))
    return Group(asset_banner(), table, Panel(ASSET_PLACEHOLDER, title="Read-only Slice", border_style="yellow"))


def _text(value: Any) -> str:
    if value is None:
        return "not configured"
    if value == "":
        return "unknown"
    return str(value)
