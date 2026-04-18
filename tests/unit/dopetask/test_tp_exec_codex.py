"""Direct task packet execution coverage for Codex and model forwarding."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from dopetask.cli import cli
from dopetask.ops.tp_exec.engine import execute_task_packet
from dopetask.ops.tp_series.logic import SeriesExecResult


def _init_repo(path: Path) -> Path:
    path.mkdir()
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True, capture_output=True, text=True)
    return path


def _write_json_packet(
    path: Path,
    *,
    expected_files: list[str],
    validation: list[str],
    commands: list[str] | None = None,
) -> Path:
    payload = {
        "id": "TP-CODEX-TEST",
        "target": "codex execution",
        "project": "dopetask",
        "steps": [
            {
                "id": "S1",
                "task": "Create the expected file",
                "requirements": ["Use deterministic content."],
                "commands": commands or [],
                "expected_files": expected_files,
                "validation": validation,
                "context_files": [],
            }
        ],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def test_execute_task_packet_codex_creates_expected_files_and_bundle(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    packet = _write_json_packet(
        repo / "packet.json",
        expected_files=["generated.txt"],
        validation=["test -f generated.txt", "grep -q ok generated.txt"],
        commands=["printf 'command-ran\\n' > command.log"],
    )
    original_run = subprocess.run

    def fake_run(argv, *args, **kwargs):
        if isinstance(argv, list) and argv[:2] == ["codex", "exec"]:
            output_index = argv.index("-o") + 1
            Path(argv[output_index]).write_text("codex output\n", encoding="utf-8")
            (repo / "generated.txt").write_text("ok\n", encoding="utf-8")
            return subprocess.CompletedProcess(argv, 0, "codex ok\n", "")
        return original_run(argv, *args, **kwargs)

    monkeypatch.setattr("dopetask_adapters.codex.executor.subprocess.run", fake_run)
    monkeypatch.setattr(
        "dopetask.router.planner.build_route_plan",
        lambda **_: SimpleNamespace(status="ok", steps=(SimpleNamespace(model="gpt-5.3-codex"),)),
    )

    bundle_path = execute_task_packet(packet, agent="codex", model="gpt-5.3-codex", working_dir=repo)

    proof = json.loads((repo / "proof" / "TP-CODEX-TEST_PROOF.json").read_text(encoding="utf-8"))
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    step = proof["steps"][0]
    assert proof["effective_model"] == "gpt-5.3-codex"
    assert step["files_created"] == ["generated.txt"]
    assert step["commands_run"] == ["printf 'command-ran\\n' > command.log"]
    assert "generated.txt" in step["changed_files"]
    assert bundle["status"] == "VALIDATED"
    assert "generated.txt" in bundle["artifacts"]["supporting"]


def test_execute_task_packet_codex_fails_closed_on_validation(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    packet = _write_json_packet(
        repo / "packet.json",
        expected_files=["missing.txt"],
        validation=["test -f missing.txt"],
    )
    original_run = subprocess.run

    def fake_run(argv, *args, **kwargs):
        if isinstance(argv, list) and argv[:2] == ["codex", "exec"]:
            output_index = argv.index("-o") + 1
            Path(argv[output_index]).write_text("codex output\n", encoding="utf-8")
            return subprocess.CompletedProcess(argv, 0, "codex ok\n", "")
        return original_run(argv, *args, **kwargs)

    monkeypatch.setattr("dopetask_adapters.codex.executor.subprocess.run", fake_run)

    with pytest.raises(RuntimeError, match="failed one or more steps"):
        execute_task_packet(packet, agent="codex", working_dir=repo)

    proof = json.loads((repo / "proof" / "TP-CODEX-TEST_PROOF.json").read_text(encoding="utf-8"))
    assert proof["steps"][0]["validation_passed"] is False
    assert proof["steps"][0]["files_created"] == []


def test_tp_exec_cli_forwards_model_override(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    packet = _write_json_packet(repo / "packet.json", expected_files=[], validation=["true"])
    captured: dict[str, object] = {}

    def fake_execute(tp_file: Path, *, agent: str, model: str | None = None, working_dir: Path | None = None) -> Path:
        captured["tp_file"] = tp_file
        captured["agent"] = agent
        captured["model"] = model
        captured["working_dir"] = working_dir
        proof_dir = repo / "proof"
        proof_dir.mkdir(parents=True, exist_ok=True)
        bundle = proof_dir / "TP-CODEX-TEST_PROOF_BUNDLE.json"
        bundle.write_text('{"tp_id":"TP-CODEX-TEST","status":"VALIDATED"}\n', encoding="utf-8")
        return bundle

    monkeypatch.setattr("dopetask.ops.tp_exec.cli.execute_task_packet", fake_execute)
    runner = CliRunner()
    result = runner.invoke(cli, ["tp", "exec", str(packet), "--agent", "codex", "--model", "gpt-5.3-codex"])

    assert result.exit_code == 0, result.stdout
    assert captured["agent"] == "codex"
    assert captured["model"] == "gpt-5.3-codex"


def test_tp_series_cli_forwards_model_override(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    packet = _write_json_packet(repo / "packet.json", expected_files=[], validation=["true"])
    captured: dict[str, object] = {}

    def fake_exec_series_packet(*, tp_file: Path, agent: str, model: str | None = None, force: bool = False, repo: Path | None = None):
        del force
        captured["tp_file"] = tp_file
        captured["agent"] = agent
        captured["model"] = model
        captured["repo"] = repo
        return SeriesExecResult(
            repo_root=repo or Path.cwd(),
            series_id="SERIES",
            tp_id="TP-CODEX-TEST",
            branch="branch",
            worktree_path=Path("/tmp/worktree"),
            run_dir=Path("/tmp/run"),
            proof_bundle=Path("/tmp/proof.json"),
            message="series packet completed: TP-CODEX-TEST",
        )

    monkeypatch.setattr("dopetask.ops.tp_series.cli.exec_series_packet", fake_exec_series_packet)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["tp", "series", "exec", str(packet), "--agent", "codex", "--model", "gpt-5.3-codex", "--repo", str(repo)],
    )

    assert result.exit_code == 0, result.stdout
    assert captured["agent"] == "codex"
    assert captured["model"] == "gpt-5.3-codex"
