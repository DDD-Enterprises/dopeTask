"""Runner health contract tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from typer.testing import CliRunner

from dopetask.cli import cli
from dopetask.ui import THEMES
from dopetask.ui.runner_health import collect_runner_health, runner_health_output_path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "dopetask_schemas" / "runner_health.schema.json"


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validator() -> Draft202012Validator:
    schema = _schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _write_availability(repo_root: Path) -> None:
    availability = repo_root / ".dopetask" / "runtime" / "availability.yaml"
    availability.parent.mkdir(parents=True, exist_ok=True)
    availability.write_text(
        """
models:
  gpt-5.3-codex:
    strengths: [code_edit]
    cost_tier: high
    context: large
runners:
  claude_code:
    available: true
    strengths: [code_edit]
  codex_desktop:
    available: true
    strengths: [code_edit]
  copilot_cli:
    available: true
    strengths: [quick_commands]
  google_jules:
    available: false
    strengths: [reasoning]
policy:
  require_explain: true
  stop_on_ambiguity: true
  max_cost_tier: high
  escalation_ladder: [gpt-5.3-codex]
  max_escalations: 1
  min_total_score: 50
""".lstrip(),
        encoding="utf-8",
    )


def test_runner_health_schema_is_valid_json_schema() -> None:
    Draft202012Validator.check_schema(_schema())


def test_collect_runner_health_returns_schema_valid_payload(tmp_path: Path) -> None:
    payload = collect_runner_health(tmp_path)

    errors = sorted(_validator().iter_errors(payload), key=lambda error: list(error.path))

    assert errors == []
    assert payload["schema_version"] == "1.0"
    assert payload["refreshed"] is False


def test_missing_availability_config_marks_configured_missing_config(tmp_path: Path) -> None:
    payload = collect_runner_health(tmp_path)

    assert payload["runners"]["claude_code"]["configured"] == "missing-config"
    assert payload["runners"]["codex_desktop"]["configured"] == "missing-config"


def test_binary_presence_uses_shutil_which(tmp_path: Path, monkeypatch) -> None:
    from dopetask.ui import runner_health

    def fake_which(binary_name: str) -> str | None:
        if binary_name == "claude":
            return "/fake/bin/claude"
        return None

    monkeypatch.setattr(runner_health.shutil, "which", fake_which)

    payload = collect_runner_health(tmp_path)

    assert payload["runners"]["claude_code"]["binary_present"] is True
    assert payload["runners"]["claude_code"]["binary_path"] == "/fake/bin/claude"
    assert payload["runners"]["codex_desktop"]["binary_present"] is False


def test_auth_ready_defaults_unknown_and_never_true(tmp_path: Path, monkeypatch) -> None:
    from dopetask.ui import runner_health

    monkeypatch.setattr(runner_health.shutil, "which", lambda binary_name: f"/fake/bin/{binary_name}")

    payload = collect_runner_health(tmp_path)

    assert {runner["auth_ready"] for runner in payload["runners"].values()} == {"unknown"}
    assert all(runner["auth_ready"] is not True for runner in payload["runners"].values())


def test_overall_health_is_not_healthy_when_auth_unknown(tmp_path: Path, monkeypatch) -> None:
    from dopetask.ui import runner_health

    _write_availability(tmp_path)
    monkeypatch.setattr(runner_health.shutil, "which", lambda binary_name: f"/fake/bin/{binary_name}")

    payload = collect_runner_health(tmp_path)

    assert payload["runners"]["codex_desktop"]["configured"] is True
    assert payload["runners"]["codex_desktop"]["binary_present"] is True
    assert payload["runners"]["codex_desktop"]["auth_ready"] == "unknown"
    assert payload["runners"]["codex_desktop"]["overall_health"] != "healthy"


def test_route_plane_not_implemented_and_missing_states_are_visible(tmp_path: Path) -> None:
    payload = collect_runner_health(tmp_path)

    assert payload["runners"]["claude_code"]["route_plane_adapter"] == "RUNNER_NOT_IMPLEMENTED"
    assert payload["runners"]["copilot_cli"]["route_plane_adapter"] == "RUNNER_NOT_IMPLEMENTED"
    assert payload["runners"]["google_jules"]["route_plane_adapter"] == "RUNNER_NOT_IMPLEMENTED"
    assert payload["runners"]["codex_desktop"]["route_plane_adapter"] == "implemented"
    assert payload["runners"]["gemini"]["route_plane_adapter"] == "missing"


def test_default_collection_does_not_write_runner_health_artifact(tmp_path: Path) -> None:
    output_path = runner_health_output_path(tmp_path)

    payload = collect_runner_health(tmp_path)

    assert payload["refreshed"] is False
    assert not output_path.exists()


def test_refresh_writes_only_runner_health_artifact(tmp_path: Path) -> None:
    before = {path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()}

    payload = collect_runner_health(tmp_path, refresh=True)

    after = {path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()}
    output_path = runner_health_output_path(tmp_path)
    assert payload["refreshed"] is True
    assert output_path.exists()
    assert after - before == {Path("out/dopetask_ui/RUNNER_HEALTH.json")}
    assert json.loads(output_path.read_text(encoding="utf-8"))["schema_version"] == "1.0"


def test_cli_runners_json_emits_parseable_json_without_writing(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli, ["ui", "runners", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["refreshed"] is False
    assert not runner_health_output_path(tmp_path).exists()


def test_cli_runners_refresh_json_writes_artifact_and_emits_parseable_json(
    tmp_path: Path,
    monkeypatch,
) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli, ["ui", "runners", "--refresh", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    output_path = runner_health_output_path(tmp_path)
    assert payload["refreshed"] is True
    assert output_path.exists()
    assert json.loads(output_path.read_text(encoding="utf-8")) == payload


def test_legacy_ui_imports_still_work() -> None:
    assert "mintwave" in THEMES


def test_no_forbidden_ui_runtime_imports_or_invocations() -> None:
    checked_paths = [
        REPO_ROOT / "src" / "dopetask" / "ui" / "__init__.py",
        REPO_ROOT / "src" / "dopetask" / "ui" / "runner_health.py",
        Path(__file__),
    ]
    forbidden_parts = [
        ("import ", "textual"),
        ("from ", "textual"),
        ("dopetask ", "doctor"),
        ("route ", "plan"),
        ("tp series ", "exec"),
    ]
    for path in checked_paths:
        text = path.read_text(encoding="utf-8")
        for phrase in ("".join(parts) for parts in forbidden_parts):
            assert phrase not in text
