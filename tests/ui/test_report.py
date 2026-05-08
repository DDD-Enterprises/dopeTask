"""Markdown report rendering contract tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

import dopetask.cli as cli_module
from dopetask.cli import cli
from dopetask.ui.report import ReportSeriesNotFoundError, render_series_report

SERIES_ID = "SERIES-REPORT-001"
TP_ID = "TP-REPORT-001"


def _durability(path: str, label: str = "local-only-gitignored") -> dict[str, Any]:
    return {
        "path": path,
        "durability": label,
        "path_kind": "repo-relative",
        "exists": True,
    }


def _status_payload(
    repo_root: Path,
    *,
    auth_mode: str | None = "api-key",
    agent: str = "codex",
    das_path: str | None = None,
    runner_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet: dict[str, Any] = {
        "tp_id": TP_ID,
        "status": "completed",
        "branch": "codex/report",
        "head_sha": "a" * 40,
        "agent": agent,
        "model": "gpt-5.3-codex",
        "requested_model": "gpt-5.3-codex",
        "effective_model": "gpt-5.3-codex",
        "effective_model_source": "explicit_override",
        "auth_mode": auth_mode or "unknown",
        "bare_mode_used": None,
        "proof_bundle_path": "out/tp_series/SERIES-REPORT-001/packets/TP-REPORT-001/TP-REPORT-001_PROOF_BUNDLE.json",
        "proof_bundle_status": "VALIDATED",
        "durability": {
            "packet_state": _durability("task-packets/TP-REPORT-001.json", "tracked-in-git"),
            "series_context": _durability("out/tp_series/SERIES-REPORT-001/packets/TP-REPORT-001/SERIES_CONTEXT.json"),
            "exec": _durability("out/tp_series/SERIES-REPORT-001/packets/TP-REPORT-001/EXEC.json"),
            "exec_error": _durability("out/tp_series/SERIES-REPORT-001/packets/TP-REPORT-001/EXEC_ERROR.json"),
            "proof_bundle": _durability(
                "out/tp_series/SERIES-REPORT-001/packets/TP-REPORT-001/TP-REPORT-001_PROOF_BUNDLE.json"
            ),
        },
        "exec_error_present": True,
        "exec_error_is_current_state": False,
        "errors": [],
    }
    return {
        "schema_version": "1.0",
        "generated_at": "2026-05-08T00:00:00Z",
        "repo_root": str(repo_root),
        "dopetask_version": "0.0-test",
        "das_path": das_path,
        "das_configured": das_path is not None,
        "version_drift": "unknown",
        "git": {
            "branch": "main",
            "head_sha": "b" * 40,
            "clean": True,
            "dirty_files": [],
            "worktrees": [],
            "stash_count": 0,
        },
        "runner_health": {
            "present": runner_payload is not None,
            "path": str(repo_root / "out" / "dopetask_ui" / "RUNNER_HEALTH.json"),
            "durability": _durability("out/dopetask_ui/RUNNER_HEALTH.json", "missing"),
            "payload": runner_payload,
            "summary": {},
            "schema_valid": True,
            "schema_errors": [],
        },
        "series": [
            {
                "series_id": SERIES_ID,
                "state_path": "out/tp_series/SERIES-REPORT-001/SERIES_STATE.json",
                "durability": _durability("out/tp_series/SERIES-REPORT-001/SERIES_STATE.json"),
                "schema_valid": True,
                "schema_errors": [],
                "status_counts": {"completed": 1, "failed": 0, "running": 0, "pending": 0},
                "last_updated": "2026-05-08T00:01:00Z",
                "pr_url": None,
                "pr": None,
                "packets": [packet],
                "errors": [],
            }
        ],
        "doctor_report_cached": False,
        "doctor_report_path": str(repo_root / "out" / "dopetask_doctor" / "DOCTOR_REPORT.json"),
        "doctor_report_durability": _durability("out/dopetask_doctor/DOCTOR_REPORT.json", "missing"),
        "doctor_report_status": "unknown",
        "route_plan_cached": False,
        "route_plan_path": str(repo_root / "out" / "dopetask_route" / "ROUTE_PLAN.json"),
        "route_plan_durability": _durability("out/dopetask_route/ROUTE_PLAN.json", "missing"),
        "errors": [],
        "warnings": [],
    }


def test_render_series_report_returns_title_and_series_id(tmp_path: Path) -> None:
    markdown = render_series_report(_status_payload(tmp_path), SERIES_ID)

    assert f"# dopeTask Series Report: {SERIES_ID}" in markdown


def test_packets_table_includes_durability_column(tmp_path: Path) -> None:
    markdown = render_series_report(_status_payload(tmp_path), SERIES_ID)

    assert "| TP ID | Status | Agent | Model | Auth Mode | Bare Mode | Branch | SHA | Proof | Durability |" in markdown


def test_packets_table_renders_missing_auth_honestly(tmp_path: Path) -> None:
    forbidden = "".join(("sub", "scription"))
    markdown = render_series_report(_status_payload(tmp_path, auth_mode=None), SERIES_ID)

    assert "Auth Mode" in markdown
    assert "unknown" in markdown
    assert forbidden not in markdown


def test_local_only_gitignored_label_appears(tmp_path: Path) -> None:
    markdown = render_series_report(_status_payload(tmp_path), SERIES_ID)

    assert "local-only-gitignored" in markdown


def test_missing_series_id_raises_clear_error(tmp_path: Path) -> None:
    try:
        render_series_report(_status_payload(tmp_path), "SERIES-MISSING")
    except ReportSeriesNotFoundError as exc:
        message = str(exc)
    else:
        raise AssertionError("missing series should raise")

    assert "SERIES-MISSING" in message
    assert SERIES_ID in message


def test_historical_exec_error_note_renders_when_completed(tmp_path: Path) -> None:
    markdown = render_series_report(_status_payload(tmp_path), SERIES_ID)

    assert "historical evidence" in markdown
    assert "not the current failure state" in markdown


def test_runner_health_summary_renders_unknown_when_absent(tmp_path: Path) -> None:
    markdown = render_series_report(_status_payload(tmp_path, runner_payload=None), SERIES_ID)

    assert "| unknown | unknown |" in markdown


def test_safety_footer_is_present(tmp_path: Path) -> None:
    markdown = render_series_report(_status_payload(tmp_path), SERIES_ID)

    assert "Generated from read-only UiStatus. This report is not proof by itself." in markdown
    assert "Local-only artifacts are not durable" in markdown


def test_markdown_table_escaping_handles_pipe_characters(tmp_path: Path) -> None:
    markdown = render_series_report(_status_payload(tmp_path, agent="codex|pipe"), SERIES_ID)

    assert "codex\\|pipe" in markdown


def test_report_cli_stdout_emits_markdown_without_writes(monkeypatch: Any, tmp_path: Path) -> None:
    runner = CliRunner()

    def fake_collect_status(repo_root: Path, **_: Any) -> dict[str, Any]:
        return _status_payload(Path(repo_root))

    monkeypatch.setattr(cli_module, "collect_status", fake_collect_status)
    with runner.isolated_filesystem(temp_dir=tmp_path):
        before = sorted(Path(".").rglob("*"))
        result = runner.invoke(cli, ["report", SERIES_ID])
        after = sorted(Path(".").rglob("*"))

    assert result.exit_code == 0, result.output
    assert f"# dopeTask Series Report: {SERIES_ID}" in result.output
    assert after == before


def test_report_cli_out_writes_only_requested_file(monkeypatch: Any, tmp_path: Path) -> None:
    runner = CliRunner()
    output_path = tmp_path / "reports" / "report.md"

    def fake_collect_status(repo_root: Path, **_: Any) -> dict[str, Any]:
        return _status_payload(Path(repo_root))

    monkeypatch.setattr(cli_module, "collect_status", fake_collect_status)
    result = runner.invoke(cli, ["report", SERIES_ID, "--out", str(output_path)])

    assert result.exit_code == 0, result.output
    assert output_path.exists()
    assert sorted(path for path in tmp_path.rglob("*") if path.is_file()) == [output_path]


def test_report_cli_out_under_proof_is_refused(monkeypatch: Any, tmp_path: Path) -> None:
    runner = CliRunner()

    def fake_collect_status(repo_root: Path, **_: Any) -> dict[str, Any]:
        return _status_payload(Path(repo_root))

    monkeypatch.setattr(cli_module, "collect_status", fake_collect_status)
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["report", SERIES_ID, "--out", "proof/report.md"])

    assert result.exit_code != 0
    assert "proof/" in result.output


def test_report_cli_out_under_das_is_refused(monkeypatch: Any, tmp_path: Path) -> None:
    runner = CliRunner()
    das = tmp_path / "fake-das"
    output_path = das / "report.md"

    def fake_collect_status(repo_root: Path, **kwargs: Any) -> dict[str, Any]:
        supplied_das = kwargs.get("das_path")
        return _status_payload(Path(repo_root), das_path=str(supplied_das) if supplied_das else None)

    monkeypatch.setattr(cli_module, "collect_status", fake_collect_status)
    result = runner.invoke(cli, ["report", SERIES_ID, "--das-path", str(das), "--out", str(output_path)])

    assert result.exit_code != 0
    assert "dope-agent-system" in result.output
    assert not output_path.exists()


def test_report_command_source_has_no_forbidden_invocations() -> None:
    report_source = Path("src/dopetask/ui/report.py").read_text(encoding="utf-8")

    for phrase in [
        " ".join(("dopetask", "doctor")),
        " ".join(("route", "plan")),
        " ".join(("tp", "series", "exec")),
    ]:
        assert phrase not in report_source


def test_no_text_ui_dependency_is_introduced() -> None:
    report_source = Path("src/dopetask/ui/report.py").read_text(encoding="utf-8")
    tests_source = Path(__file__).read_text(encoding="utf-8")

    for phrase in [" ".join(("import", "textual")), " ".join(("from", "textual"))]:
        assert phrase not in report_source
        assert phrase not in tests_source


def test_fixture_payload_is_json_serializable(tmp_path: Path) -> None:
    json.dumps(_status_payload(tmp_path), sort_keys=True)
