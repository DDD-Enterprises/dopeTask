from __future__ import annotations

from rich.console import Console

from dopetask.ui.widgets.banners import (
    ASSET_BANNER_LINE_1,
    ASSET_BANNER_LINE_2,
    PLANNING_BANNER,
    REFERENCE_BANNER,
    RUNTIME_BANNER,
    asset_banner,
    planning_banner,
    reference_banner,
    runtime_banner,
)


def _render_text(renderable: object) -> str:
    console = Console(record=True, width=120, color_system=None)
    console.print(renderable)
    return console.export_text()


def test_runtime_banner_text_is_present() -> None:
    assert RUNTIME_BANNER in _render_text(runtime_banner())


def test_asset_banner_text_is_present() -> None:
    output = _render_text(asset_banner())

    assert ASSET_BANNER_LINE_1 in output
    assert ASSET_BANNER_LINE_2 in output


def test_reference_banner_text_is_present() -> None:
    assert REFERENCE_BANNER in _render_text(reference_banner())


def test_planning_banner_text_is_present() -> None:
    assert PLANNING_BANNER in _render_text(planning_banner())
