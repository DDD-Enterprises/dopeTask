from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

from rich.console import Console
from typer.testing import CliRunner

import dopetask.cli as cli_module
from dopetask.cli import cli
from dopetask.ui import cockpit as cockpit_module
from dopetask.ui.cockpit import render_cockpit
from dopetask.ui.views.asset_library import render_asset_library
from dopetask.ui.views.authority_diff import render_authority_diff
from dopetask.ui.views.packet_detail import render_packet_detail
from dopetask.ui.views.runner_health import render_runner_health
from dopetask.ui.views.series_overview import render_series_overview


SERIES_ID = "SERIES-COCKPIT-001"
TP_ID = "TP-COCKPIT-001"


def _durability(path: str, label: str = "local-only-gitignored") -> dict[str, Any]:
    return {
        "path": path,
        "durability": label,
        "path_kind": "repo-relative",
        "exists": True,
    }


def _status_payload(repo_root: Path, *, auth_mode: str | None = "api-key", series: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    packet = {
        "tp_id": TP_ID,
        "status": "completed",
        "branch": "codex/cockpit",
        "head_sha": "a" * 40,
        "agent": "codex",
        "model": "gpt-5.3-codex",
        "requested_model": "gpt-5.3-codex",
        "effective_model": "gpt-5.3-codex",
        "effective_model_source": "explicit_override",
        "auth_mode": auth_mode or "unknown",
        "bare_mode_used": None,
        "proof_bundle_path": "out/tp_series/SERIES-COCKPIT-001/packets/TP-COCKPIT-001/TP-COCKPIT-001_PROOF_BUNDLE.json",
        "proof_bundle_status": "VALIDATED",
        "durability": {
            "packet_state": _durability("task-packets/TP-COCKPIT-001.json", "tracked-in-git"),
            "series_context": _durability("out/tp_series/SERIES-COCKPIT-001/packets/TP-COCKPIT-001/SERIES_CONTEXT.json"),
            "exec": _durability("out/tp_series/SERIES-COCKPIT-001/packets/TP-COCKPIT-001/EXEC.json"),
            "exec_error": _durability("out/tp_series/SERIES-COCKPIT-001/packets/TP-COCKPIT-001/EXEC_ERROR.json"),
            "proof_bundle": _durability("out/tp_series/SERIES-COCKPIT-001/packets/TP-COCKPIT-001/TP-COCKPIT-001_PROOF_BUNDLE.json"),
        },
        "exec_error_present": True,
        "exec_error_is_current_state": False,
        "errors": [],
    }
    default_series = [
        {
            "series_id": SERIES_ID,
            "state_path": "out/tp_series/SERIES-COCKPIT-001/SERIES_STATE.json",
            "durability": _durability("out/tp_series/SERIES-COCKPIT-001/SERIES_STATE.json"),
            "schema_valid": True,
            "schema_errors": [],
            "status_counts": {"completed": 1, "failed": 0, "running": 0, "pending": 0},
            "last_updated": "2026-05-08T00:01:00Z",
            "pr_url": None,
            "pr": None,
            "packets": [packet],
            "errors": [],
        }
    ]
    return {
        "schema_version": "1.0",
        "generated_at": "2026-05-08T00:00:00Z",
        "repo_root": str(repo_root),
        "dopetask_version": "0.0-test",
        "das_path": str(repo_root / "dope-agent-system"),
        "das_configured": True,
        "version_drift": "unknown",
        "git": {
            "branch": "main",
            "head_sha": "b" * 40,
            "clean": True,
            "dirty_files": [],
            "worktrees": [{"path": str(repo_root), "head": "b" * 40, "branch": "main"}],
            "stash_count": 0,
        },
        "runner_health": {
            "present": True,
            "path": str(repo_root / "out" / "dopetask_ui" / "RUNNER_HEALTH.json"),
            "durability": _durability("out/dopetask_ui/RUNNER_HEALTH.json", "missing"),
            "payload": {
                "runners": {
                    "claude_code": {
                        "configured": True,
                        "binary_present": False,
                        "auth_ready": "unknown",
                        "tp_series_adapter": "implemented",
                        "route_plane_adapter": "RUNNER_NOT_IMPLEMENTED",
                        "overall_health": "degraded",
                        "notes": ["route-plane adapter is not implemented"],
                    }
                }
            },
            "summary": {},
            "schema_valid": True,
            "schema_errors": [],
        },
        "series": default_series if series is None else series,
        "doctor_report_cached": False,
        "doctor_report_path": str(repo_root / "out" / "dopetask_doctor" / "DOCTOR_REPORT.json"),
        "doctor_report_durability": _durability("out/dopetask_doctor/DOCTOR_REPORT.json", "missing"),
        "doctor_report_status": "unknown",
        "route_plan_cached": False,
        "route_plan_path": str(repo_root / "out" / "dopetask_route" / "ROUTE_PLAN.json"),
        "route_plan_durability": _durability("out/dopetask_route/ROUTE_PLAN.json", "missing"),
        "errors": [{"path": "out/example.json", "message": "schema invalid"}],
        "warnings": [{"message": "reference drift requires remediation"}],
    }


def _render_text(renderable: object) -> str:
    console = Console(record=True, width=160, color_system=None)
    console.print(renderable)
    return console.export_text()


def test_cockpit_help_succeeds() -> None:
    result = CliRunner().invoke(cli, ["cockpit", "--help"])

    assert result.exit_code == 0, result.output
    assert "--view" in result.output


def test_cockpit_series_overview_renders_runtime_banner(monkeypatch: Any, tmp_path: Path) -> None:
    monkeypatch.setattr(cockpit_module, "collect_status", lambda *args, **kwargs: _status_payload(tmp_path))

    result = CliRunner().invoke(cli, ["cockpit", "--view", "series-overview", "--no-color"])

    assert result.exit_code == 0, result.output
    assert "[Runtime / Execution Authority" in result.output


def test_runner_health_view_renders_runner_axes(tmp_path: Path) -> None:
    output = _render_text(render_runner_health(_status_payload(tmp_path)))

    assert "configured" in output
    assert "binary_present" in output
    assert "auth_ready" in output
    assert "tp_series_adapter" in output
    assert "route_plane_adapter" in output


def test_repo_health_view_renders_git_fields(tmp_path: Path) -> None:
    output = _render_text(render_cockpit(_status_payload(tmp_path), view="repo-health"))

    assert "branch" in output
    assert "head_sha" in output
    assert "clean" in output
    assert "dirty_files" in output
    assert "worktrees" in output
    assert "stash_count" in output


def test_asset_library_view_renders_asset_banner_without_affordances(tmp_path: Path) -> None:
    output = _render_text(render_asset_library(_status_payload(tmp_path)))

    assert "ASSET / TEMPLATE PLANE" in output
    for forbidden in ("Run", "Install", "Execute", "Apply"):
        assert forbidden not in output


def test_authority_diff_view_renders_reference_banner_without_apply_action(tmp_path: Path) -> None:
    output = _render_text(render_authority_diff(_status_payload(tmp_path)))

    assert "[Reference" in output
    assert "Authority diff is read-only" in output
    assert "Apply" not in output


def test_all_view_includes_all_titles(tmp_path: Path) -> None:
    output = _render_text(render_cockpit(_status_payload(tmp_path), view="all"))

    for title in (
        "Series Overview",
        "Series Detail",
        "Packet Detail",
        "Runner Health",
        "Repo Health",
        "Asset Library",
        "Authority Diff",
    ):
        assert title in output


def test_view_renderers_consume_fixture_payloads_without_file_reads() -> None:
    import dopetask.ui.views.asset_library as asset_library
    import dopetask.ui.views.authority_diff as authority_diff
    import dopetask.ui.views.packet_detail as packet_detail
    import dopetask.ui.views.repo_health as repo_health
    import dopetask.ui.views.runner_health as runner_health
    import dopetask.ui.views.series_detail as series_detail
    import dopetask.ui.views.series_overview as series_overview

    for module in (
        asset_library,
        authority_diff,
        packet_detail,
        repo_health,
        runner_health,
        series_detail,
        series_overview,
    ):
        source = inspect.getsource(module)
        assert ".read_text(" not in source
        assert ".open(" not in source
        assert "collect_status" not in source


def test_missing_series_renders_empty_state(tmp_path: Path) -> None:
    output = _render_text(render_series_overview(_status_payload(tmp_path, series=[])))

    assert "No series found" in output


def test_missing_auth_mode_renders_unknown(tmp_path: Path) -> None:
    output = _render_text(render_packet_detail(_status_payload(tmp_path, auth_mode=None), SERIES_ID, TP_ID))

    assert "auth_mode" in output
    assert "unknown" in output
    forbidden = "".join(("sub", "scription"))
    assert forbidden not in output


def test_runner_not_implemented_remains_visible(tmp_path: Path) -> None:
    output = _render_text(render_runner_health(_status_payload(tmp_path)))

    assert "RUNNER_NOT_IMPLEMENTED" in output


def test_historical_exec_error_note_is_visible(tmp_path: Path) -> None:
    output = _render_text(render_cockpit(_status_payload(tmp_path), view="series-detail", series_id=SERIES_ID))

    assert "EXEC_ERROR is historical evidence" in output
    assert "not current state" in output


def test_no_forbidden_tui_imports_in_new_ui_code() -> None:
    root = Path(__file__).resolve().parents[3]
    checked = [
        root / "src" / "dopetask" / "ui" / "cockpit.py",
        *(root / "src" / "dopetask" / "ui" / "views").glob("*.py"),
        *(root / "src" / "dopetask" / "ui" / "widgets").glob("*.py"),
    ]
    package_name = "".join(chr(code) for code in (116, 101, 120, 116, 117, 97, 108))
    forbidden = (f"import {package_name}", f"from {package_name}")
    for path in checked:
        source = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in source


def test_no_mutating_command_strings_in_new_ui_code_or_tests() -> None:
    root = Path(__file__).resolve().parents[3]
    checked = [
        root / "src" / "dopetask" / "ui" / "cockpit.py",
        *(root / "src" / "dopetask" / "ui" / "views").glob("*.py"),
        *(root / "src" / "dopetask" / "ui" / "widgets").glob("*.py"),
        Path(__file__),
    ]
    forbidden = (
        " ".join(("dopetask", "doctor")),
        " ".join(("route", "plan")),
        " ".join(("tp", "series", "exec")),
    )
    for path in checked:
        source = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in source


def test_cockpit_command_smoke_writes_no_files(monkeypatch: Any, tmp_path: Path) -> None:
    monkeypatch.setattr(cockpit_module, "collect_status", lambda *args, **kwargs: _status_payload(tmp_path))
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        before = sorted(path.relative_to(Path.cwd()) for path in Path.cwd().rglob("*") if path.is_file())
        result = runner.invoke(cli, ["cockpit", "--view", "series-overview", "--no-color"])
        after = sorted(path.relative_to(Path.cwd()) for path in Path.cwd().rglob("*") if path.is_file())

    assert result.exit_code == 0, result.output
    assert after == before


def test_cli_module_uses_cockpit_collector_once(monkeypatch: Any, tmp_path: Path) -> None:
    calls = 0

    def fake_collect_status(*args: Any, **kwargs: Any) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        return _status_payload(tmp_path)

    monkeypatch.setattr(cockpit_module, "collect_status", fake_collect_status)
    result = CliRunner().invoke(cli_module.cli, ["cockpit", "--view", "all", "--no-color"])

    assert result.exit_code == 0, result.output
    assert calls == 1
