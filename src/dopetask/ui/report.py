"""Markdown reports rendered from read-only UiStatus payloads."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional


SAFETY_FOOTER = (
    "Generated from read-only UiStatus. This report is not proof by itself. "
    "Runtime proof remains in dopeTask proof/series artifacts."
)


class ReportSeriesNotFoundError(ValueError):
    """Raised when a requested series is absent from a UiStatus payload."""


class ReportOutputRefusedError(ValueError):
    """Raised when a requested report output path crosses a safety boundary."""


def find_series(status_payload: dict[str, Any], series_id: str) -> Optional[dict[str, Any]]:
    """Return the requested series summary from a UiStatus payload."""

    for series in status_payload.get("series", []):
        if isinstance(series, dict) and series.get("series_id") == series_id:
            return series
    return None


def render_series_report(status_payload: dict[str, Any], series_id: str) -> str:
    """Render a deterministic markdown report for one series."""

    series = find_series(status_payload, series_id)
    if series is None:
        available = sorted(
            str(item.get("series_id"))
            for item in status_payload.get("series", [])
            if isinstance(item, dict) and item.get("series_id")
        )
        suffix = ", ".join(available) if available else "none"
        raise ReportSeriesNotFoundError(f"Series '{series_id}' not found. Available series ids: {suffix}")

    git = status_payload.get("git") if isinstance(status_payload.get("git"), dict) else {}
    lines: list[str] = [
        f"# dopeTask Series Report: {_text(series_id)}",
        "",
        "## Generated Metadata",
        f"- generated_at: {_text(status_payload.get('generated_at'))}",
        f"- repo_root: {_text(status_payload.get('repo_root'))}",
        f"- dopeTask version: {_text(status_payload.get('dopetask_version'))}",
        f"- git branch: {_text(git.get('branch'))}",
        f"- git head: {_text(git.get('head_sha'))}",
        f"- git clean: {_text(git.get('clean'))}",
        f"- DAS configured: {_text(status_payload.get('das_configured'))}",
        f"- DAS path: {_text(status_payload.get('das_path'))}",
        "",
        "## Status Summary",
    ]
    counts = series.get("status_counts") if isinstance(series.get("status_counts"), dict) else {}
    lines.extend(
        [
            "| Completed | Failed | Running | Pending | Last Updated | PR |",
            "| --- | --- | --- | --- | --- | --- |",
            (
                f"| {_cell(counts.get('completed', 0))} | {_cell(counts.get('failed', 0))} | "
                f"{_cell(counts.get('running', 0))} | {_cell(counts.get('pending', 0))} | "
                f"{_cell(series.get('last_updated'))} | {_cell(_pr_summary(series))} |"
            ),
            "",
            "## Packets",
            "| TP ID | Status | Agent | Model | Auth Mode | Bare Mode | Branch | SHA | Proof | Durability |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    packets = [packet for packet in series.get("packets", []) if isinstance(packet, dict)]
    for packet in packets:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(packet.get("tp_id")),
                    _cell(packet.get("status")),
                    _cell(packet.get("agent")),
                    _cell(_model_summary(packet)),
                    _cell(packet.get("auth_mode") or "unknown"),
                    _cell(_bare_mode(packet.get("bare_mode_used"))),
                    _cell(packet.get("branch")),
                    _cell(_short_sha(packet.get("head_sha"))),
                    _cell(packet.get("proof_bundle_status") or "unknown"),
                    _cell(_packet_durability_summary(packet)),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Artifact Durability"])
    lines.extend(_artifact_durability_lines(series, packets))

    lines.extend(["", "## Runner Health"])
    lines.extend(_runner_health_lines(status_payload.get("runner_health")))

    lines.extend(["", "## Warnings and Errors"])
    lines.extend(_warning_error_lines(status_payload, series, packets))

    lines.extend(
        [
            "",
            "## Safety",
            SAFETY_FOOTER,
            "Local-only artifacts are not durable unless committed or exported elsewhere.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(path: Path, markdown: str, *, repo_root: Path, das_path: Optional[Path] = None) -> None:
    """Write markdown to an explicit path after safety boundary checks."""

    output_path = _resolve_under_caller(path, repo_root)
    resolved_repo_root = repo_root.resolve()
    proof_root = resolved_repo_root / "proof"
    if _is_relative_to(output_path, proof_root):
        raise ReportOutputRefusedError("--out under proof/ is refused for report output")

    if das_path is not None:
        resolved_das_path = _resolve_under_caller(das_path, repo_root)
        if _is_relative_to(output_path, resolved_das_path):
            raise ReportOutputRefusedError("--out under resolved dope-agent-system path is refused")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")


def _artifact_durability_lines(series: dict[str, Any], packets: list[dict[str, Any]]) -> list[str]:
    lines = [
        "### Series",
        "| Artifact | Path | Durability | Path Kind |",
        "| --- | --- | --- | --- |",
        _durability_row("SERIES_STATE", series.get("durability")),
        "",
        "### Packets",
        "| TP ID | Artifact | Path | Durability | Path Kind |",
        "| --- | --- | --- | --- | --- |",
    ]
    for packet in packets:
        durability = packet.get("durability") if isinstance(packet.get("durability"), dict) else {}
        for artifact_name in ["packet_state", "series_context", "exec", "exec_error", "proof_bundle"]:
            lines.append(_packet_durability_row(packet.get("tp_id"), artifact_name, durability.get(artifact_name)))
    return lines


def _runner_health_lines(runner_health: Any) -> list[str]:
    if not isinstance(runner_health, dict):
        return ["| Runner | Overall Health |", "| --- | --- |", "| unknown | unknown |"]
    payload = runner_health.get("payload") if isinstance(runner_health.get("payload"), dict) else None
    runners = payload.get("runners") if isinstance(payload, dict) and isinstance(payload.get("runners"), dict) else {}
    lines = ["| Runner | Overall Health |", "| --- | --- |"]
    if not runners:
        lines.append("| unknown | unknown |")
        return lines
    for name, details in sorted(runners.items()):
        if isinstance(details, dict):
            overall_health = details.get("overall_health") or "unknown"
        else:
            overall_health = "unknown"
        lines.append(f"| {_cell(name)} | {_cell(overall_health)} |")
    return lines


def _warning_error_lines(
    status_payload: dict[str, Any],
    series: dict[str, Any],
    packets: list[dict[str, Any]],
) -> list[str]:
    entries: list[str] = []
    entries.extend(_markers("UiStatus warning", status_payload.get("warnings")))
    entries.extend(_markers("UiStatus error", status_payload.get("errors")))
    entries.extend(_markers("Series schema error", series.get("schema_errors")))
    entries.extend(_markers("Series error", series.get("errors")))
    for packet in packets:
        tp_id = _text(packet.get("tp_id"))
        entries.extend(_markers(f"{tp_id} error", packet.get("errors")))
        if packet.get("exec_error_present") and not packet.get("exec_error_is_current_state"):
            entries.append(
                f"- {tp_id}: EXEC_ERROR.json is historical evidence and is not the current failure state."
            )
    if not entries:
        return ["- none"]
    return entries


def _markers(prefix: str, markers: Any) -> list[str]:
    if not isinstance(markers, list):
        return []
    lines: list[str] = []
    for marker in markers:
        if isinstance(marker, dict):
            path = marker.get("path")
            message = marker.get("message")
            lines.append(f"- {_text(prefix)}: {_text(message)} ({_text(path)})")
        else:
            lines.append(f"- {_text(prefix)}: {_text(marker)}")
    return lines


def _durability_row(name: str, durability: Any) -> str:
    if not isinstance(durability, dict):
        return f"| {_cell(name)} | unknown | missing | unknown |"
    return (
        f"| {_cell(name)} | {_cell(durability.get('path'))} | "
        f"{_cell(durability.get('durability'))} | {_cell(durability.get('path_kind'))} |"
    )


def _packet_durability_row(tp_id: Any, name: str, durability: Any) -> str:
    if not isinstance(durability, dict):
        return f"| {_cell(tp_id)} | {_cell(name)} | unknown | missing | unknown |"
    return (
        f"| {_cell(tp_id)} | {_cell(name)} | {_cell(durability.get('path'))} | "
        f"{_cell(durability.get('durability'))} | {_cell(durability.get('path_kind'))} |"
    )


def _packet_durability_summary(packet: dict[str, Any]) -> str:
    durability = packet.get("durability") if isinstance(packet.get("durability"), dict) else {}
    parts: list[str] = []
    for key in ["proof_bundle", "exec", "series_context", "exec_error"]:
        info = durability.get(key)
        if isinstance(info, dict):
            parts.append(f"{key}={info.get('durability') or 'unknown'}")
    return "; ".join(parts) if parts else "unknown"


def _model_summary(packet: dict[str, Any]) -> str:
    return _text(packet.get("effective_model") or packet.get("model") or packet.get("requested_model"))


def _bare_mode(value: Any) -> str:
    if value is None:
        return "unknown"
    return _text(value)


def _pr_summary(series: dict[str, Any]) -> str:
    if series.get("pr_url"):
        return _text(series.get("pr_url"))
    pr = series.get("pr")
    if isinstance(pr, dict) and pr:
        return ", ".join(f"{key}={value}" for key, value in sorted(pr.items()))
    return "unknown"


def _short_sha(value: Any) -> str:
    text = _text(value)
    if text == "unknown":
        return text
    return text[:12]


def _cell(value: Any) -> str:
    return _text(value).replace("|", "\\|").replace("\n", " ")


def _text(value: Any) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _resolve_under_caller(path: Path, repo_root: Path) -> Path:
    expanded = path.expanduser()
    if not expanded.is_absolute():
        expanded = repo_root.resolve() / expanded
    return expanded.resolve()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True
