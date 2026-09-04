"""Runner health cockpit view."""

from __future__ import annotations

from typing import Any

from rich.console import Group
from rich.table import Table

from dopetask.ui.widgets.banners import runtime_banner


def render_runner_health(
    status_payload: dict[str, Any],
    series_id: str | None = None,
    tp_id: str | None = None,
) -> Group:
    del series_id, tp_id
    table = Table(title="Runner Health")
    for column in (
        "runner",
        "configured",
        "binary_present",
        "auth_ready",
        "tp_series_adapter",
        "route_plane_adapter",
        "overall_health",
        "notes",
    ):
        table.add_column(column)

    runner_health = _dict(status_payload.get("runner_health"))
    payload = _dict(runner_health.get("payload"))
    runners = _dict(payload.get("runners"))
    if runners:
        for name, details in sorted(runners.items()):
            row = _dict(details)
            notes = row.get("notes") if isinstance(row.get("notes"), list) else []
            table.add_row(
                _text(name),
                _text(row.get("configured")),
                _text(row.get("binary_present")),
                _text(row.get("auth_ready")),
                _text(row.get("tp_series_adapter")),
                _text(row.get("route_plane_adapter")),
                _text(row.get("overall_health")),
                "; ".join(str(item) for item in notes) if notes else "none",
            )
    else:
        table.add_row("unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "not configured")

    return Group(runtime_banner(), table)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _text(value: Any) -> str:
    if value is None:
        return "unknown"
    if value == "":
        return "unknown"
    return str(value)
