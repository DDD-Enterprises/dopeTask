"""Read-only UI status collector."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

from jsonschema import Draft202012Validator, FormatChecker

from dopetask import __version__
from dopetask.ui.durability import classify_artifact_path
from dopetask.ui.runner_health import collect_runner_health, runner_health_output_path
from dopetask.workspace import WorkspaceConfigError, resolve_dope_agent_system_path

SCHEMA_VERSION = "1.0"
OUT_DIR = Path("out")
TP_SERIES_DIR = OUT_DIR / "tp_series"
ROUTE_PLAN_PATH = OUT_DIR / "dopetask_route" / "ROUTE_PLAN.json"
DOCTOR_REPORT_PATH = OUT_DIR / "dopetask_doctor" / "DOCTOR_REPORT.json"

SCHEMA_FILES = {
    "series_state": Path("dopetask_schemas") / "series_state.schema.json",
    "exec_record": Path("dopetask_schemas") / "exec_record.schema.json",
    "exec_error": Path("dopetask_schemas") / "exec_error.schema.json",
    "series_context": Path("dopetask_schemas") / "series_context.schema.json",
    "route_plan": Path("dopetask_schemas") / "route_plan.schema.json",
    "runner_health": Path("dopetask_schemas") / "runner_health.schema.json",
}


def collect_status(
    repo_root: Path,
    *,
    refresh_runner_health: bool = False,
    das_path: Optional[Union[Path, str]] = None,
) -> dict[str, Any]:
    """Collect read-only UI status from cached runtime artifacts."""

    resolved_repo_root = repo_root.resolve()
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    resolved_das_path = _resolve_das_path(resolved_repo_root, das_path, warnings)
    _append_cached_route_plan_errors(resolved_repo_root, errors)

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "repo_root": str(resolved_repo_root),
        "dopetask_version": __version__,
        "das_path": str(resolved_das_path) if resolved_das_path is not None else None,
        "das_configured": resolved_das_path is not None,
        "version_drift": "unknown",
        "git": _git_status(resolved_repo_root, errors),
        "runner_health": _runner_health_status(resolved_repo_root, refresh_runner_health, errors),
        "series": _series_statuses(resolved_repo_root),
        "doctor_report_cached": (resolved_repo_root / DOCTOR_REPORT_PATH).exists(),
        "doctor_report_path": str(resolved_repo_root / DOCTOR_REPORT_PATH),
        "doctor_report_durability": classify_artifact_path(resolved_repo_root, resolved_repo_root / DOCTOR_REPORT_PATH),
        "doctor_report_status": _doctor_report_status(resolved_repo_root, errors),
        "route_plan_cached": (resolved_repo_root / ROUTE_PLAN_PATH).exists(),
        "route_plan_path": str(resolved_repo_root / ROUTE_PLAN_PATH),
        "route_plan_durability": classify_artifact_path(resolved_repo_root, resolved_repo_root / ROUTE_PLAN_PATH),
        "errors": errors,
        "warnings": warnings,
    }
    return payload


def status_output_path_for_repo(repo_root: Path) -> Path:
    """Return the conventional status output path for explicit writers."""

    return repo_root.resolve() / OUT_DIR / "dopetask_ui" / "STATUS.json"


def _series_statuses(repo_root: Path) -> list[dict[str, Any]]:
    series_root = repo_root / TP_SERIES_DIR
    if not series_root.exists():
        return []

    results: list[dict[str, Any]] = []
    for state_path in sorted(series_root.glob("*/SERIES_STATE.json")):
        results.append(_series_status(repo_root, state_path))
    return results


def _series_status(repo_root: Path, state_path: Path) -> dict[str, Any]:
    payload, schema_errors = _load_json_with_schema(repo_root, state_path, "series_state")
    state_durability = classify_artifact_path(repo_root, state_path)
    fallback_series_id = state_path.parent.name
    if not isinstance(payload, dict):
        return {
            "series_id": fallback_series_id,
            "state_path": str(state_path),
            "durability": state_durability,
            "schema_valid": False,
            "schema_errors": schema_errors,
            "status_counts": _empty_status_counts(),
            "last_updated": None,
            "pr_url": None,
            "pr": None,
            "packets": [],
            "errors": [{"path": str(state_path), "message": "SERIES_STATE.json is not usable"}],
        }

    packets_raw = payload.get("packets")
    packets = packets_raw if isinstance(packets_raw, dict) else {}
    packet_summaries = [
        _packet_status(repo_root, state_path.parent, tp_id, record if isinstance(record, dict) else {})
        for tp_id, record in sorted(packets.items())
    ]
    pr = payload.get("pr") if isinstance(payload.get("pr"), dict) else None

    return {
        "series_id": str(payload.get("series_id") or fallback_series_id),
        "state_path": str(state_path),
        "durability": state_durability,
        "schema_valid": not schema_errors,
        "schema_errors": schema_errors,
        "status_counts": _status_counts(packets),
        "last_updated": payload.get("updated_at"),
        "pr_url": pr.get("url") if pr else None,
        "pr": pr,
        "packets": packet_summaries,
        "errors": [] if not schema_errors else [{"path": str(state_path), "message": "schema invalid"}],
    }


def _packet_status(repo_root: Path, series_dir: Path, tp_id: str, state_record: dict[str, Any]) -> dict[str, Any]:
    packet_dir = series_dir / "packets" / tp_id
    exec_path = packet_dir / "EXEC.json"
    exec_error_path = packet_dir / "EXEC_ERROR.json"
    context_path = packet_dir / "SERIES_CONTEXT.json"
    proof_bundle_path = _proof_bundle_path(packet_dir, state_record)

    exec_payload, exec_schema_errors = _load_json_with_schema(repo_root, exec_path, "exec_record")
    exec_error_payload, exec_error_schema_errors = _load_json_with_schema(repo_root, exec_error_path, "exec_error")
    _, context_schema_errors = _load_json_with_schema(repo_root, context_path, "series_context")

    exec_record = exec_payload if isinstance(exec_payload, dict) else {}
    current_status = state_record.get("status")
    exec_error_present = exec_error_path.exists()
    exec_error_is_current_state = bool(
        current_status == "failed"
        and exec_error_present
        and isinstance(exec_error_payload, dict)
        and exec_error_payload.get("tp_id") == tp_id
    )
    errors = _artifact_errors(exec_path, exec_schema_errors)
    errors.extend(_artifact_errors(exec_error_path, exec_error_schema_errors))
    errors.extend(_artifact_errors(context_path, context_schema_errors))

    return {
        "tp_id": str(state_record.get("tp_id") or tp_id),
        "status": current_status or "unknown",
        "branch": state_record.get("branch") or exec_record.get("branch"),
        "head_sha": state_record.get("head_sha") or exec_record.get("head_sha"),
        "agent": exec_record.get("agent"),
        "model": exec_record.get("model"),
        "requested_model": exec_record.get("requested_model"),
        "effective_model": exec_record.get("effective_model"),
        "effective_model_source": exec_record.get("effective_model_source"),
        "auth_mode": exec_record.get("auth_mode") or "unknown",
        "bare_mode_used": exec_record.get("bare_mode_used"),
        "proof_bundle_path": str(proof_bundle_path) if proof_bundle_path is not None else None,
        "proof_bundle_status": _proof_bundle_status(proof_bundle_path),
        "durability": {
            "packet_state": classify_artifact_path(repo_root, state_record.get("packet_path")),
            "series_context": classify_artifact_path(repo_root, context_path),
            "exec": classify_artifact_path(repo_root, exec_path),
            "exec_error": classify_artifact_path(repo_root, exec_error_path),
            "proof_bundle": classify_artifact_path(repo_root, proof_bundle_path),
        },
        "exec_error_present": exec_error_present,
        "exec_error_is_current_state": exec_error_is_current_state,
        "errors": errors,
    }


def _runner_health_status(
    repo_root: Path,
    refresh_runner_health: bool,
    errors: list[dict[str, Any]],
) -> dict[str, Any]:
    path = runner_health_output_path(repo_root)
    if refresh_runner_health:
        payload = collect_runner_health(repo_root, refresh=True)
        return {
            "present": True,
            "path": str(path),
            "durability": classify_artifact_path(repo_root, path),
            "payload": payload,
            "summary": _runner_health_summary(payload),
            "schema_valid": True,
            "schema_errors": [],
        }

    payload, schema_errors = _load_json_with_schema(repo_root, path, "runner_health")
    if schema_errors:
        errors.append({"path": str(path), "message": "runner health schema invalid", "errors": schema_errors})
    usable_payload = payload if isinstance(payload, dict) and not schema_errors else None
    return {
        "present": path.exists(),
        "path": str(path),
        "durability": classify_artifact_path(repo_root, path),
        "payload": usable_payload,
        "summary": _runner_health_summary(usable_payload),
        "schema_valid": not schema_errors,
        "schema_errors": schema_errors,
    }


def _doctor_report_status(repo_root: Path, errors: list[dict[str, Any]]) -> str:
    path = repo_root / DOCTOR_REPORT_PATH
    if not path.exists():
        return "unknown"
    payload, load_errors = _load_json(path)
    if load_errors:
        errors.append({"path": str(path), "message": "doctor report JSON invalid", "errors": load_errors})
        return "unknown"
    if isinstance(payload, dict):
        status = payload.get("status") or payload.get("overall_status")
        if status in {"passed", "failed", "unknown"}:
            return str(status)
    return "unknown"


def _append_cached_route_plan_errors(repo_root: Path, errors: list[dict[str, Any]]) -> None:
    path = repo_root / ROUTE_PLAN_PATH
    if not path.exists():
        return
    _, schema_errors = _load_json_with_schema(repo_root, path, "route_plan")
    if schema_errors:
        errors.append({"path": str(path), "message": "route-plan schema invalid", "errors": schema_errors})


def _git_status(repo_root: Path, errors: list[dict[str, Any]]) -> dict[str, Any]:
    branch = _git_stdout(repo_root, ["git", "rev-parse", "--abbrev-ref", "HEAD"], errors)
    head_sha = _git_stdout(repo_root, ["git", "rev-parse", "HEAD"], errors)
    dirty_output = _git_stdout(repo_root, ["git", "status", "--short"], errors)
    worktrees_output = _git_stdout(repo_root, ["git", "worktree", "list", "--porcelain"], errors)
    stash_output = _git_stdout(repo_root, ["git", "stash", "list"], errors)
    dirty_files = [line for line in dirty_output.splitlines() if line]
    return {
        "branch": branch or "unknown",
        "head_sha": head_sha or None,
        "clean": len(dirty_files) == 0,
        "dirty_files": dirty_files,
        "worktrees": _parse_worktrees(worktrees_output),
        "stash_count": len([line for line in stash_output.splitlines() if line]),
    }


def _parse_worktrees(output: str) -> list[dict[str, Any]]:
    worktrees: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for line in output.splitlines():
        if not line:
            if current:
                worktrees.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            current["path"] = value
        elif key == "HEAD":
            current["head_sha"] = value
        elif key == "branch":
            current["branch"] = value.removeprefix("refs/heads/")
        elif key == "bare":
            current["bare"] = True
        elif key == "detached":
            current["detached"] = True
    if current:
        worktrees.append(current)
    return worktrees


def _git_stdout(repo_root: Path, command: list[str], errors: list[dict[str, Any]]) -> str:
    result = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        errors.append(
            {
                "path": str(repo_root),
                "message": f"git command failed: {' '.join(command)}",
                "stderr": result.stderr.strip(),
            }
        )
        return ""
    return result.stdout.strip()


def _load_json_with_schema(repo_root: Path, path: Path, schema_name: str) -> tuple[Any, list[dict[str, Any]]]:
    if not path.exists():
        return None, []
    payload, errors = _load_json(path)
    if errors:
        return payload, errors
    schema_path = repo_root / SCHEMA_FILES[schema_name]
    schema_payload, schema_load_errors = _load_json(schema_path)
    if schema_load_errors:
        return payload, schema_load_errors
    validator = Draft202012Validator(schema_payload, format_checker=FormatChecker())
    schema_errors = [
        {
            "path": "/".join(str(part) for part in error.path) or "<root>",
            "message": error.message,
        }
        for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.path))
    ]
    return payload, schema_errors


def _load_json(path: Path) -> tuple[Any, list[dict[str, Any]]]:
    if not path.exists():
        return None, []
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [{"path": "<json>", "message": str(exc)}]


def _resolve_das_path(
    repo_root: Path,
    explicit_path: Optional[Union[Path, str]],
    warnings: list[dict[str, Any]],
) -> Optional[Path]:
    try:
        return resolve_dope_agent_system_path(repo_root, explicit_path=explicit_path)
    except WorkspaceConfigError as exc:
        warnings.append({"path": str(repo_root / ".dopetask" / "workspace.yaml"), "message": str(exc)})
        return None


def _proof_bundle_path(packet_dir: Path, state_record: dict[str, Any]) -> Optional[Path]:
    state_path = state_record.get("proof_bundle")
    if isinstance(state_path, str) and state_path:
        return Path(state_path)
    matches = sorted(packet_dir.glob("*_PROOF_BUNDLE.json"))
    if matches:
        return matches[0]
    return None


def _proof_bundle_status(path: Optional[Path]) -> str:
    if path is None or not path.exists():
        return "missing"
    payload, errors = _load_json(path)
    if errors or not isinstance(payload, dict):
        return "invalid"
    status = payload.get("status")
    return str(status) if status is not None else "unknown"


def _status_counts(packets: dict[str, Any]) -> dict[str, int]:
    counts = _empty_status_counts()
    for record in packets.values():
        if not isinstance(record, dict):
            continue
        status = record.get("status")
        if status in counts:
            counts[status] += 1
    return counts


def _empty_status_counts() -> dict[str, int]:
    return {"completed": 0, "failed": 0, "running": 0, "pending": 0}


def _artifact_errors(path: Path, schema_errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not schema_errors:
        return []
    return [{"path": str(path), "message": "schema invalid", "errors": schema_errors}]


def _runner_health_summary(payload: Optional[dict[str, Any]]) -> dict[str, Any]:
    if not payload:
        return {"runner_count": 0, "overall_health_counts": {}}
    runners = payload.get("runners")
    if not isinstance(runners, dict):
        return {"runner_count": 0, "overall_health_counts": {}}
    counts: dict[str, int] = {}
    for runner in runners.values():
        if not isinstance(runner, dict):
            continue
        health = str(runner.get("overall_health", "unknown"))
        counts[health] = counts.get(health, 0) + 1
    return {"runner_count": len(runners), "overall_health_counts": counts}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
