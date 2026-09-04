"""Read-only cockpit view renderers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from rich.console import Group, RenderableType

from dopetask.ui.views.asset_library import render_asset_library
from dopetask.ui.views.authority_diff import render_authority_diff
from dopetask.ui.views.packet_detail import render_packet_detail
from dopetask.ui.views.repo_health import render_repo_health
from dopetask.ui.views.runner_health import render_runner_health
from dopetask.ui.views.series_detail import render_series_detail
from dopetask.ui.views.series_overview import render_series_overview

ViewRenderer = Callable[[dict[str, Any], str | None, str | None], RenderableType]

VIEW_ORDER: tuple[str, ...] = (
    "series-overview",
    "series-detail",
    "packet-detail",
    "runner-health",
    "repo-health",
    "asset-library",
    "authority-diff",
)

VIEW_RENDERERS: dict[str, ViewRenderer] = {
    "series-overview": render_series_overview,
    "series-detail": render_series_detail,
    "packet-detail": render_packet_detail,
    "runner-health": render_runner_health,
    "repo-health": render_repo_health,
    "asset-library": render_asset_library,
    "authority-diff": render_authority_diff,
}


def render_all(status_payload: dict[str, Any], series_id: str | None, tp_id: str | None) -> Group:
    return Group(
        *[
            VIEW_RENDERERS[name](status_payload, series_id, tp_id)
            for name in VIEW_ORDER
        ]
    )


__all__ = [
    "VIEW_ORDER",
    "VIEW_RENDERERS",
    "ViewRenderer",
    "render_all",
]
