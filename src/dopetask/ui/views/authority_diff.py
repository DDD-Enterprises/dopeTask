"""Read-only authority diff cockpit placeholder."""

from __future__ import annotations

from typing import Any

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from dopetask.ui.widgets.banners import reference_banner


AUTHORITY_DIFF_MESSAGE = "Authority diff is read-only. No reference contract can update runtime behavior from this view."
DRIFT_WARNING = "Reference drift requires a remediation TP before runtime behavior can change."


def render_authority_diff(
    status_payload: dict[str, Any],
    series_id: str | None = None,
    tp_id: str | None = None,
) -> Group:
    del series_id, tp_id
    table = Table(title="Authority Diff")
    table.add_column("field")
    table.add_column("value")
    table.add_row("UiStatus schema_version", _text(status_payload.get("schema_version")))
    table.add_row("proof/status schema availability", _schema_availability(status_payload))
    table.add_row("runner health schema", _schema_status(status_payload.get("runner_health")))
    table.add_row("workspace schema", "available")
    table.add_row("status errors", _list_state(status_payload.get("errors")))
    table.add_row("status warnings", _list_state(status_payload.get("warnings")))
    return Group(
        reference_banner(),
        table,
        Panel(DRIFT_WARNING, title="Reference Drift", border_style="yellow"),
        Panel(AUTHORITY_DIFF_MESSAGE, title="Read-only Authority", border_style="cyan"),
    )


def _schema_status(value: Any) -> str:
    if isinstance(value, dict):
        schema_valid = value.get("schema_valid")
        if schema_valid is True:
            return "available"
        if schema_valid is False:
            return "schema error"
    return "unknown"


def _schema_availability(status_payload: dict[str, Any]) -> str:
    if status_payload.get("schema_version"):
        return "UiStatus schema version present; proof schema availability is not exposed by UiStatus"
    return "not exposed by UiStatus"


def _list_state(value: Any) -> str:
    if isinstance(value, list):
        return "none" if not value else str(len(value))
    return "unknown"


def _text(value: Any) -> str:
    if value is None:
        return "unknown"
    if value == "":
        return "unknown"
    return str(value)
