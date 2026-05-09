"""UI status collector contract tests."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from typer.testing import CliRunner

from dopetask.cli import cli
from dopetask.ui.durability import classify_artifact_path
from dopetask.ui.runner_health import runner_health_output_path
from dopetask.ui.status import collect_status

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "dopetask_schemas" / "ui_status.schema.json"
REQUIRED_RUNTIME_SCHEMAS = [
    "series_state.schema.json",
    "exec_record.schema.json",
    "exec_error.schema.json",
    "series_context.schema.json",
    "runner_health.schema.json",
]


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validator() -> Draft202012Validator:
    schema = _schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _assert_schema_valid(payload: dict[str, Any]) -> None:
    errors = sorted(_validator().iter_errors(payload), key=lambda error: list(error.path))
    assert errors == []


def _copy_runtime_schemas(repo_root: Path) -> None:
    schema_dir = repo_root / "dopetask_schemas"
    schema_dir.mkdir()
    for filename in REQUIRED_RUNTIME_SCHEMAS:
        shutil.copy(REPO_ROOT / "dopetask_schemas" / filename, schema_dir / filename)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _series_state(status: str = "completed") -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "series_id": "SERIES-STATUS-001",
        "base_branch": "main",
        "created_at": "2026-05-08T00:00:00Z",
        "updated_at": "2026-05-08T00:01:00Z",
        "packets": {
            "TP-STATUS-001": {
                "tp_id": "TP-STATUS-001",
                "packet_path": "task-packets/TP-STATUS-001.json",
                "branch": "codex/status",
                "base_ref": "main",
                "depends_on": [],
                "parent_tp_id": None,
                "final_packet": True,
                "status": status,
                "worktree_path": "/tmp/status-worktree",
                "run_dir": "out/tp_series/SERIES-STATUS-001/packets/TP-STATUS-001",
                "started_at": "2026-05-08T00:00:00Z",
                "updated_at": "2026-05-08T00:01:00Z",
                "completed_at": "2026-05-08T00:01:00Z",
                "head_sha": "a" * 40,
                "proof_bundle": "out/tp_series/SERIES-STATUS-001/packets/TP-STATUS-001/TP-STATUS-001_PROOF_BUNDLE.json",
                "error": None,
            }
        },
        "pr": None,
    }


def _exec_record(*, include_auth_mode: bool = True) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "series_id": "SERIES-STATUS-001",
        "tp_id": "TP-STATUS-001",
        "branch": "codex/status",
        "base_ref": "main",
        "packet_path": "task-packets/TP-STATUS-001.json",
        "bundle_path": "proof/TP-STATUS-001/PROOF.json",
        "copied_proof_bundle": None,
        "agent": "codex",
        "model": "gpt-5.3-codex",
        "requested_model": "gpt-5.3-codex",
        "effective_model": "gpt-5.3-codex",
        "effective_model_source": "explicit_override",
        "bare_mode_used": False,
        "verify": [],
        "committed_files": [],
        "context": {
            "schema_version": "1.0",
            "series_id": "SERIES-STATUS-001",
            "tp_id": "TP-STATUS-001",
            "parent_tp_id": None,
            "depends_on": [],
            "dependencies": {},
        },
        "head_sha": "b" * 40,
    }
    if include_auth_mode:
        payload["auth_mode"] = "api-key"
    return payload


def _series_context() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "series_id": "SERIES-STATUS-001",
        "tp_id": "TP-STATUS-001",
        "parent_tp_id": None,
        "depends_on": [],
        "dependencies": {},
    }


def _exec_error() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "series_id": "SERIES-STATUS-001",
        "tp_id": "TP-STATUS-001",
        "branch": "codex/status",
        "worktree_path": "/tmp/status-worktree",
        "error": "historical failure",
    }


def _write_fixture_series(repo_root: Path, *, include_auth_mode: bool = True, status: str = "completed") -> None:
    _copy_runtime_schemas(repo_root)
    series_dir = repo_root / "out" / "tp_series" / "SERIES-STATUS-001"
    packet_dir = series_dir / "packets" / "TP-STATUS-001"
    _write_json(series_dir / "SERIES_STATE.json", _series_state(status=status))
    _write_json(packet_dir / "EXEC.json", _exec_record(include_auth_mode=include_auth_mode))
    _write_json(packet_dir / "SERIES_CONTEXT.json", _series_context())
    _write_json(packet_dir / "EXEC_ERROR.json", _exec_error())
    _write_json(packet_dir / "TP-STATUS-001_PROOF_BUNDLE.json", {"status": "VALIDATED"})


def test_ui_status_schema_is_valid_json_schema() -> None:
    Draft202012Validator.check_schema(_schema())


def test_collect_status_without_series_returns_schema_valid_empty_series(tmp_path: Path) -> None:
    payload = collect_status(tmp_path)

    _assert_schema_valid(payload)
    assert payload["series"] == []


def test_collect_status_default_run_writes_no_files(tmp_path: Path) -> None:
    before = {path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()}

    collect_status(tmp_path)

    after = {path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()}
    assert after == before


def test_collect_status_includes_git_branch_head_clean_fields() -> None:
    payload = collect_status(REPO_ROOT)

    assert isinstance(payload["git"]["branch"], str)
    assert isinstance(payload["git"]["head_sha"], str)
    assert isinstance(payload["git"]["clean"], bool)


def test_collect_status_reads_series_state_and_status_counts(tmp_path: Path) -> None:
    _write_fixture_series(tmp_path)

    payload = collect_status(tmp_path)

    _assert_schema_valid(payload)
    assert payload["series"][0]["status_counts"]["completed"] == 1


def test_collect_status_reads_exec_agent_model_auth_fields(tmp_path: Path) -> None:
    _write_fixture_series(tmp_path)

    packet = collect_status(tmp_path)["series"][0]["packets"][0]

    assert packet["agent"] == "codex"
    assert packet["model"] == "gpt-5.3-codex"
    assert packet["requested_model"] == "gpt-5.3-codex"
    assert packet["effective_model"] == "gpt-5.3-codex"
    assert packet["effective_model_source"] == "explicit_override"
    assert packet["auth_mode"] == "api-key"
    assert packet["bare_mode_used"] is False


def test_missing_auth_mode_renders_unknown_never_subscription(tmp_path: Path) -> None:
    _write_fixture_series(tmp_path, include_auth_mode=False)

    packet = collect_status(tmp_path)["series"][0]["packets"][0]

    assert packet["auth_mode"] == "unknown"
    assert packet["auth_mode"] != "subscription"


def test_exec_error_presence_alone_is_not_current_failure(tmp_path: Path) -> None:
    _write_fixture_series(tmp_path, status="completed")

    packet = collect_status(tmp_path)["series"][0]["packets"][0]

    assert packet["exec_error_present"] is True
    assert packet["exec_error_is_current_state"] is False


def test_invalid_series_state_marks_schema_error_without_crashing(tmp_path: Path) -> None:
    _copy_runtime_schemas(tmp_path)
    state_path = tmp_path / "out" / "tp_series" / "BAD-SERIES" / "SERIES_STATE.json"
    _write_json(state_path, {"schema_version": "1.0", "series_id": "BAD-SERIES"})

    payload = collect_status(tmp_path)

    _assert_schema_valid(payload)
    assert payload["series"][0]["schema_valid"] is False
    assert payload["series"][0]["schema_errors"]


def test_invalid_exec_marks_packet_error_without_crashing(tmp_path: Path) -> None:
    _write_fixture_series(tmp_path)
    exec_path = tmp_path / "out" / "tp_series" / "SERIES-STATUS-001" / "packets" / "TP-STATUS-001" / "EXEC.json"
    _write_json(exec_path, {"schema_version": "1.0", "tp_id": "TP-STATUS-001"})

    packet = collect_status(tmp_path)["series"][0]["packets"][0]

    assert packet["errors"]
    assert packet["auth_mode"] == "unknown"


def test_durability_classifier_returns_tracked_for_tracked_file() -> None:
    info = classify_artifact_path(REPO_ROOT, REPO_ROOT / "dopetask_schemas" / "workspace.schema.json")

    assert info["durability"] == "tracked-in-git"


def test_durability_classifier_returns_gitignored_for_out_artifact() -> None:
    ignored_path = REPO_ROOT / "out" / "dopetask_ui" / "test_status_ignored.tmp"
    ignored_path.parent.mkdir(parents=True, exist_ok=True)
    ignored_path.write_text("ignored\n", encoding="utf-8")
    try:
        info = classify_artifact_path(REPO_ROOT, ignored_path)
    finally:
        ignored_path.unlink(missing_ok=True)

    assert info["durability"] == "local-only-gitignored"


def test_durability_classifier_returns_missing_for_missing_path(tmp_path: Path) -> None:
    info = classify_artifact_path(tmp_path, tmp_path / "missing.json")

    assert info["durability"] == "missing"


def test_cli_status_json_emits_parseable_schema_valid_json(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli, ["ui", "status", "--json"])

    assert result.exit_code == 0, result.output
    _assert_schema_valid(json.loads(result.output))


def test_cli_status_out_writes_only_requested_file(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    out_path = tmp_path / "nested" / "status.json"

    result = runner.invoke(cli, ["ui", "status", "--json", "--out", str(out_path)])

    assert result.exit_code == 0, result.output
    assert out_path.exists()
    files = {path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()}
    assert files == {Path("nested/status.json")}


def test_cli_status_refuses_outside_repo_and_does_not_create_file(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    outside_path = tmp_path / "outside-status.json"
    monkeypatch.chdir(repo_root)

    result = runner.invoke(cli, ["ui", "status", "--json", "--out", "../outside-status.json"])

    assert result.exit_code == 2
    assert "outside repository root" in result.output
    assert not outside_path.exists()


def test_cli_status_refuses_out_under_proof(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli, ["ui", "status", "--json", "--out", "proof/status.json"])

    assert result.exit_code == 2
    assert not (tmp_path / "proof" / "status.json").exists()


def test_refresh_runners_writes_only_runner_health_output(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli, ["ui", "status", "--json", "--refresh-runners"])

    assert result.exit_code == 0, result.output
    assert runner_health_output_path(tmp_path).exists()
    files = {path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()}
    assert files == {Path("out/dopetask_ui/RUNNER_HEALTH.json")}


def test_status_collector_source_does_not_reference_forbidden_invocations() -> None:
    checked_paths = [
        REPO_ROOT / "src" / "dopetask" / "ui" / "status.py",
        REPO_ROOT / "src" / "dopetask" / "ui" / "durability.py",
    ]
    forbidden = [
        " ".join(("dopetask", "doctor")),
        " ".join(("route", "plan")),
        " ".join(("tp", "series", "exec")),
    ]

    for path in checked_paths:
        text = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in text


def test_no_textual_import_or_dependency_introduced() -> None:
    checked_paths = [
        REPO_ROOT / "src" / "dopetask" / "ui" / "status.py",
        REPO_ROOT / "src" / "dopetask" / "ui" / "durability.py",
        Path(__file__),
    ]

    for path in checked_paths:
        text = path.read_text(encoding="utf-8")
        assert " ".join(("import", "textual")) not in text
        assert " ".join(("from", "textual")) not in text


def test_status_refuses_das_out_write(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    das_root = tmp_path / "das"
    das_root.mkdir()
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        cli,
        ["ui", "status", "--json", "--das-path", str(das_root), "--out", str(das_root / "status.json")],
    )

    assert result.exit_code == 2
    assert not (das_root / "status.json").exists()


def test_status_refuses_symlink_to_outside_repo(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    outside_target = tmp_path.parent / "outside-status-target.json"
    symlink_path = tmp_path / "linked-status.json"
    symlink_path.symlink_to(outside_target)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli, ["ui", "status", "--json", "--out", str(symlink_path)])

    assert result.exit_code == 2
    assert "outside repository root" in result.output
    assert not outside_target.exists()


def test_status_refuses_symlink_to_proof(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    proof_target = tmp_path / "proof" / "linked-status.json"
    proof_target.parent.mkdir()
    symlink_path = tmp_path / "linked-status.json"
    symlink_path.symlink_to(proof_target)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(cli, ["ui", "status", "--json", "--out", str(symlink_path)])

    assert result.exit_code == 2
    assert "proof/" in result.output
    assert not proof_target.exists()


def test_status_refuses_symlink_to_das(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    das_root = tmp_path / "das"
    das_target = das_root / "linked-status.json"
    das_root.mkdir()
    symlink_path = tmp_path / "linked-status.json"
    symlink_path.symlink_to(das_target)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        cli,
        ["ui", "status", "--json", "--das-path", str(das_root), "--out", str(symlink_path)],
    )

    assert result.exit_code == 2
    assert "dope-agent-system" in result.output
    assert not das_target.exists()
