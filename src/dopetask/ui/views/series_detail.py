"""Series detail cockpit view."""

from __future__ import annotations

from typing import Any

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from dopetask.ui.widgets.banners import runtime_banner


def render_series_detail(
    status_payload: dict[str, Any],
    series_id: str | None = None,
    tp_id: str | None = None,
) -> Group:
    del tp_id
    series, notice = _select_series(status_payload, series_id)
    table = Table(title="Series Detail")
    for column in (
        "tp_id",
        "status",
        "agent",
        "model/effective_model",
        "branch",
        "head_sha",
        "proof_bundle_status",
        "durability",
    ):
        table.add_column(column)

    historical_notes: list[str] = []
    if series is not None:
        for packet in _packets(series):
            durability = _dict(packet.get("durability"))
            table.add_row(
                _text(packet.get("tp_id")),
                _text(packet.get("status")),
                _text(packet.get("agent")),
                _text(packet.get("effective_model") or packet.get("model")),
                _text(packet.get("branch")),
                _short_sha(packet.get("head_sha")),
                _text(packet.get("proof_bundle_status")),
                _durability_summary(durability),
            )
            if packet.get("exec_error_present") and not packet.get("exec_error_is_current_state"):
                historical_notes.append(
                    f"{_text(packet.get('tp_id'))}: EXEC_ERROR is historical evidence and not current state."
                )
    else:
        table.add_row("missing", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "missing")

    panels = [runtime_banner()]
    if notice:
        panels.append(Panel(notice, title="Selection", border_style="yellow"))
    if series is not None:
        panels.append(Panel(f"series_id={_text(series.get('series_id'))}", title="Selected Series"))
    panels.append(table)
    if historical_notes:
        panels.append(Panel("\n".join(historical_notes), title="Historical EXEC_ERROR", border_style="yellow"))
    panels.extend(_schema_error_panels(series))
    return Group(*panels)


def _select_series(status_payload: dict[str, Any], series_id: str | None) -> tuple[dict[str, Any] | None, str | None]:
    rows = [row for row in status_payload.get("series", []) if isinstance(row, dict)]
    if series_id:
        for row in rows:
            if row.get("series_id") == series_id:
                return row, None
        return None, f"Series '{series_id}' not found."
    if len(rows) == 1:
        return rows[0], None
    if not rows:
        return None, "No series found."
    return None, "More than one series exists; pass --series-id for Series Detail."


def _packets(series: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in series.get("packets", []) if isinstance(row, dict)]


def _schema_error_panels(series: dict[str, Any] | None) -> list[Panel]:
    if series is None:
        return []
    panels: list[Panel] = []
    if series.get("schema_errors"):
        panels.append(Panel(_text(series.get("schema_errors")), title="Series schema errors", border_style="red"))
    if series.get("errors"):
        panels.append(Panel(_text(series.get("errors")), title="Series errors", border_style="red"))
    return panels


def _durability_summary(durability: dict[str, Any]) -> str:
    proof = _dict(durability.get("proof_bundle"))
    return _text(proof.get("durability"))


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _short_sha(value: Any) -> str:
    text = _text(value)
    return text[:12] if text not in {"unknown", "missing"} else text


def _text(value: Any) -> str:
    if value is None:
        return "unknown"
    if value == "":
        return "unknown"
    return str(value)
