"""Packet detail cockpit view."""

from __future__ import annotations

from typing import Any

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from dopetask.ui.widgets.banners import runtime_banner


def render_packet_detail(
    status_payload: dict[str, Any],
    series_id: str | None = None,
    tp_id: str | None = None,
) -> Group:
    packet, notice = _select_packet(status_payload, series_id, tp_id)
    fields = Table(title="Packet Detail")
    fields.add_column("field")
    fields.add_column("value")
    for name in (
        "agent",
        "model",
        "requested_model",
        "effective_model",
        "effective_model_source",
        "auth_mode",
        "bare_mode_used",
        "branch",
        "head_sha",
        "proof_bundle_status",
    ):
        fields.add_row(name, _text(packet.get(name)) if packet else "unknown")

    durability = Table(title="Artifact Durability")
    durability.add_column("artifact")
    durability.add_column("durability")
    durability.add_column("path_kind")
    durability.add_column("path")
    if packet:
        for name, details in sorted(_dict(packet.get("durability")).items()):
            row = _dict(details)
            durability.add_row(
                name,
                _text(row.get("durability")),
                _text(row.get("path_kind")),
                _text(row.get("path")),
            )
    else:
        durability.add_row("missing", "missing", "unknown", "unknown")

    panels = [runtime_banner()]
    if notice:
        panels.append(Panel(notice, title="Selection", border_style="yellow"))
    if packet and _text(packet.get("auth_mode")) == "unknown":
        panels.append(Panel("auth_mode is unknown. Billing state is not inferred.", title="Auth Mode", border_style="yellow"))
    panels.extend([fields, durability])
    if packet and packet.get("errors"):
        panels.append(Panel(_text(packet.get("errors")), title="Packet Errors", border_style="red"))
    return Group(*panels)


def _select_packet(
    status_payload: dict[str, Any],
    series_id: str | None,
    tp_id: str | None,
) -> tuple[dict[str, Any] | None, str | None]:
    series_rows = [row for row in status_payload.get("series", []) if isinstance(row, dict)]
    if series_id:
        series_rows = [row for row in series_rows if row.get("series_id") == series_id]
        if not series_rows:
            return None, f"Series '{series_id}' not found."
    if len(series_rows) > 1:
        return None, "More than one series exists; pass --series-id for Packet Detail."
    if not series_rows:
        return None, "No series found."
    packets = [row for row in series_rows[0].get("packets", []) if isinstance(row, dict)]
    if tp_id:
        for packet in packets:
            if packet.get("tp_id") == tp_id:
                return packet, None
        return None, f"Packet '{tp_id}' not found."
    if len(packets) == 1:
        return packets[0], None
    if not packets:
        return None, "No packets found."
    return None, "More than one packet exists; pass --tp-id for Packet Detail."


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _text(value: Any) -> str:
    if value is None:
        return "unknown"
    if value == "":
        return "unknown"
    return str(value)
