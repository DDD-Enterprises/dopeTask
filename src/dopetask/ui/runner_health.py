"""Read-only runner health collection for UI/report foundations."""

from __future__ import annotations

import importlib.util
import inspect
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dopetask.router.availability import AvailabilityError, availability_path_for_repo, load_availability
from dopetask.router.types import RUNNER_NAMES
from dopetask.runners import RUNNER_ADAPTERS

SCHEMA_VERSION = "1.0"
RUNNER_HEALTH_RELATIVE_PATH = Path("out") / "dopetask_ui" / "RUNNER_HEALTH.json"

TP_SERIES_ADAPTER_MODULES: dict[str, str | None] = {
    "claude_code": "claude_code",
    "codex": "codex",
    "codex_desktop": "codex",
    "copilot_cli": None,
    "gemini": "gemini",
    "google_jules": None,
}

BINARY_NAMES: dict[str, str | None] = {
    "claude_code": "claude",
    "codex": "codex",
    "codex_desktop": "codex",
    "copilot_cli": None,
    "gemini": "gemini",
    "google_jules": None,
}

KNOWN_RUNNERS: tuple[str, ...] = tuple(sorted(set(RUNNER_NAMES) | set(TP_SERIES_ADAPTER_MODULES)))


def runner_health_output_path(repo_root: Path) -> Path:
    """Return the canonical runner health artifact path for ``repo_root``."""

    return repo_root.resolve() / RUNNER_HEALTH_RELATIVE_PATH


def collect_runner_health(repo_root: Path, *, refresh: bool = False) -> dict[str, Any]:
    """Collect runner health without writing unless ``refresh`` is true."""

    resolved_repo_root = repo_root.resolve()
    configured, availability_notes = _configured_states(resolved_repo_root)
    runners: dict[str, dict[str, Any]] = {}
    for runner_name in KNOWN_RUNNERS:
        notes = list(availability_notes.get(runner_name, []))
        binary_name = BINARY_NAMES.get(runner_name)
        binary_path = shutil.which(binary_name) if binary_name else None
        if binary_name is None:
            notes.append("binary name is not confirmed by current runtime source")

        tp_series_adapter = _tp_series_adapter_state(runner_name)
        route_plane_adapter = _route_plane_adapter_state(runner_name)
        auth_ready: bool | str = "unknown"
        auth_probe_method = "not_implemented"

        runners[runner_name] = {
            "configured": configured.get(runner_name, False),
            "binary_present": binary_path is not None,
            "binary_path": binary_path,
            "auth_ready": auth_ready,
            "auth_probe_method": auth_probe_method,
            "tp_series_adapter": tp_series_adapter,
            "route_plane_adapter": route_plane_adapter,
            "overall_health": _overall_health(
                configured=configured.get(runner_name, False),
                binary_present=binary_path is not None,
                auth_ready=auth_ready,
                tp_series_adapter=tp_series_adapter,
                route_plane_adapter=route_plane_adapter,
            ),
            "notes": sorted(set(notes)),
        }

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "repo_root": str(resolved_repo_root),
        "output_path": str(runner_health_output_path(resolved_repo_root)),
        "refreshed": refresh,
        "runners": runners,
    }
    if refresh:
        write_runner_health(resolved_repo_root, payload)
    return payload


def write_runner_health(repo_root: Path, payload: dict[str, Any]) -> Path:
    """Write ``payload`` to the canonical runner health artifact path."""

    output_path = runner_health_output_path(repo_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _configured_states(repo_root: Path) -> tuple[dict[str, bool | str], dict[str, list[str]]]:
    availability_path = availability_path_for_repo(repo_root)
    if not availability_path.exists():
        return (
            {runner_name: "missing-config" for runner_name in KNOWN_RUNNERS},
            {
                runner_name: [f"availability config missing at {availability_path}"]
                for runner_name in KNOWN_RUNNERS
            },
        )

    try:
        availability = load_availability(repo_root)
    except AvailabilityError as exc:
        return (
            {runner_name: False for runner_name in KNOWN_RUNNERS},
            {
                runner_name: [f"availability config invalid: {exc.reason_code}: {exc}"]
                for runner_name in KNOWN_RUNNERS
            },
        )

    configured: dict[str, bool | str] = {}
    notes: dict[str, list[str]] = {}
    for runner_name in KNOWN_RUNNERS:
        runner_spec = availability.runners.get(runner_name)
        if runner_spec is None:
            configured[runner_name] = False
            notes[runner_name] = ["runner is not declared in availability config"]
        else:
            configured[runner_name] = bool(runner_spec.available)
            notes[runner_name] = []
    return configured, notes


def _tp_series_adapter_state(runner_name: str) -> str:
    module_name = TP_SERIES_ADAPTER_MODULES.get(runner_name)
    if module_name is None:
        return "missing"
    if importlib.util.find_spec(f"dopetask_adapters.{module_name}") is None:
        return "missing"
    return "implemented"


def _route_plane_adapter_state(runner_name: str) -> str:
    adapter_cls = RUNNER_ADAPTERS.get(runner_name)
    if adapter_cls is None:
        return "missing"
    run_method = getattr(adapter_cls, "run", None)
    if run_method is None:
        return "unknown"
    try:
        source = inspect.getsource(run_method)
    except (OSError, TypeError):
        return "unknown"
    if "RUNNER_NOT_IMPLEMENTED" in source:
        return "RUNNER_NOT_IMPLEMENTED"
    return "implemented"


def _overall_health(
    *,
    configured: bool | str,
    binary_present: bool,
    auth_ready: bool | str,
    tp_series_adapter: str,
    route_plane_adapter: str,
) -> str:
    if not binary_present:
        return "unavailable"
    if configured == "missing-config":
        return "unknown"
    if configured is not True:
        return "degraded"
    if auth_ready is not True:
        return "degraded"
    if tp_series_adapter != "implemented":
        return "degraded"
    if route_plane_adapter != "implemented":
        return "degraded"
    return "healthy"
