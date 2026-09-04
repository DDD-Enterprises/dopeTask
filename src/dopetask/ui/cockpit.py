"""Read-only rich cockpit for dopeTask.

This module intentionally stays rich-only. Textual adoption requires a separate
design decision and Task Packet. Cockpit views read one UiStatus payload and do
not mutate runtime artifacts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from rich.console import Console, Group
from rich.panel import Panel

from dopetask.ui.status import collect_status
from dopetask.ui.views import VIEW_ORDER, VIEW_RENDERERS, render_all

CockpitViewName = Literal[
    "series-overview",
    "series-detail",
    "packet-detail",
    "runner-health",
    "repo-health",
    "asset-library",
    "authority-diff",
    "all",
]


def render_cockpit(
    status_payload: dict[str, Any],
    *,
    view: str = "series-overview",
    series_id: str | None = None,
    tp_id: str | None = None,
) -> Group:
    """Render a cockpit view from one UiStatus payload."""

    if view == "all":
        return render_all(status_payload, series_id, tp_id)
    renderer = VIEW_RENDERERS.get(view)
    if renderer is None:
        valid = ", ".join((*VIEW_ORDER, "all"))
        return Group(Panel(f"Unknown cockpit view '{view}'. Valid views: {valid}", title="Cockpit Error", border_style="red"))
    return Group(renderer(status_payload, series_id, tp_id))


def run_cockpit(
    *,
    repo_root: Path,
    view: str = "series-overview",
    series_id: str | None = None,
    tp_id: str | None = None,
    refresh_runners: bool = False,
    das_path: Path | None = None,
    no_color: bool = False,
) -> None:
    """Collect UiStatus once and render the requested rich cockpit view."""

    status_payload = collect_status(
        repo_root,
        refresh_runner_health=refresh_runners,
        das_path=das_path,
    )
    console = Console(no_color=no_color)
    console.print(
        render_cockpit(
            status_payload,
            view=view,
            series_id=series_id,
            tp_id=tp_id,
        )
    )


__all__ = ["CockpitViewName", "render_cockpit", "run_cockpit"]
