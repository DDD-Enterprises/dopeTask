"""Series overview cockpit view."""

from __future__ import annotations

from typing import Any

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from dopetask.ui.widgets.banners import runtime_banner


def render_series_overview(
    status_payload: dict[str, Any],
    series_id: str | None = None,
    tp_id: str | None = None,
) -> Group:
    del series_id, tp_id
    git = _dict(status_payload.get("git"))
    table = Table(title="Series Overview")
    for column in ("series_id", "completed", "failed", "running", "pending", "last_updated", "durability"):
        table.add_column(column)

    series_rows = [row for row in status_payload.get("series", []) if isinstance(row, dict)]
    if series_rows:
        for series in series_rows:
            counts = _dict(series.get("status_counts"))
            durability = _dict(series.get("durability"))
            table.add_row(
                _text(series.get("series_id")),
                _text(counts.get("completed", 0)),
                _text(counts.get("failed", 0)),
                _text(counts.get("running", 0)),
                _text(counts.get("pending", 0)),
                _text(series.get("last_updated")),
                _text(durability.get("durability")),
            )
    else:
        table.add_row("missing", "0", "0", "0", "0", "unknown", "missing")

    metadata = Table.grid(padding=(0, 2))
    metadata.add_column("field")
    metadata.add_column("value")
    metadata.add_row("Repo root", _text(status_payload.get("repo_root")))
    metadata.add_row("dopeTask version", _text(status_payload.get("dopetask_version")))
    metadata.add_row("Git branch", _text(git.get("branch")))
    metadata.add_row("Git head", _text(git.get("head_sha")))
    metadata.add_row("Git clean", _text(git.get("clean")))

    messages = []
    if not series_rows:
        messages.append(Panel("No series found in UiStatus.", title="Empty State", border_style="yellow"))
    messages.extend(_warning_panels(status_payload))
    return Group(runtime_banner(), Panel(metadata, title="Runtime"), table, *messages)


def _warning_panels(status_payload: dict[str, Any]) -> list[Panel]:
    panels: list[Panel] = []
    for label in ("warnings", "errors"):
        rows = status_payload.get(label)
        if isinstance(rows, list) and rows:
            panels.append(Panel(_text(rows), title=f"UiStatus {label}", border_style="red"))
    return panels


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _text(value: Any) -> str:
    if value is None:
        return "unknown"
    if value == "":
        return "unknown"
    return str(value)
