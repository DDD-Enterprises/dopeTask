"""Repository health cockpit view."""

from __future__ import annotations

from typing import Any

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from dopetask.ui.widgets.banners import runtime_banner


def render_repo_health(
    status_payload: dict[str, Any],
    series_id: str | None = None,
    tp_id: str | None = None,
) -> Group:
    del series_id, tp_id
    git = _dict(status_payload.get("git"))
    table = Table(title="Repo Health")
    table.add_column("field")
    table.add_column("value")
    table.add_row("branch", _text(git.get("branch")))
    table.add_row("head_sha", _text(git.get("head_sha")))
    table.add_row("clean", _text(git.get("clean")))
    table.add_row("dirty_files", _list_text(git.get("dirty_files")))
    table.add_row("worktrees", _list_text(git.get("worktrees")))
    table.add_row("stash_count", _text(git.get("stash_count")))
    table.add_row("doctor_report_cached", _text(status_payload.get("doctor_report_cached")))
    table.add_row("doctor_report_path", _text(status_payload.get("doctor_report_path")))
    table.add_row("doctor_report_status", _text(status_payload.get("doctor_report_status")))

    if status_payload.get("doctor_report_cached"):
        doctor_message = "Cached doctor report is present in UiStatus."
    else:
        doctor_message = "No cached doctor report found. Generate one outside cockpit if needed."
    return Group(runtime_banner(), table, Panel(doctor_message, title="Cached Doctor Report"))


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_text(value: Any) -> str:
    if not isinstance(value, list):
        return "unknown"
    if not value:
        return "none"
    return "; ".join(str(item) for item in value)


def _text(value: Any) -> str:
    if value is None:
        return "unknown"
    if value == "":
        return "unknown"
    return str(value)
