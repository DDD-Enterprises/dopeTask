"""Authority-plane banners for read-only cockpit views.

These banners are safety requirements, not decoration. They keep runtime,
asset/reference, and planning planes visually distinct.
"""

from __future__ import annotations

from rich.panel import Panel
from rich.text import Text

RUNTIME_BANNER = "[Runtime / Execution Authority — dopeTask]"
ASSET_BANNER_LINE_1 = "ASSET / TEMPLATE PLANE — dope-agent-system"
ASSET_BANNER_LINE_2 = "NOT runtime authority. Cannot authorize execution."
REFERENCE_BANNER = "[Reference — read-only, cannot override runtime]"
PLANNING_BANNER = "[Planning Plane — PAL/clink output. Not proof. Not authority.]"


def runtime_banner() -> Panel:
    return Panel(Text(RUNTIME_BANNER, style="bold green"), border_style="green")


def asset_banner() -> Panel:
    text = Text()
    text.append(ASSET_BANNER_LINE_1, style="bold yellow")
    text.append("\n")
    text.append(ASSET_BANNER_LINE_2, style="bold red")
    return Panel(text, border_style="yellow")


def reference_banner() -> Panel:
    return Panel(Text(REFERENCE_BANNER, style="bold cyan"), border_style="cyan")


def planning_banner() -> Panel:
    return Panel(Text(PLANNING_BANNER, style="bold magenta"), border_style="magenta")
