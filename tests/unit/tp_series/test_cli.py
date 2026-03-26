"""Tests for DAG-aware JSON TP series execution."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from dopetask.cli import cli
from dopetask.ops.tp_git.exec import ExecResult


def _output_text(result) -> str:
    return f"{result.stdout}{getattr(result, 'stderr', '')}"


def _git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _init_repo_with_origin(tmp_path: Path) -> Path:
    remote = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / "README.md").write_text("# repo\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "initial")
    _git(repo, "branch", "-M", "main")
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "-u", "origin", "main")
    return repo


def _write_packet(
    path: Path,
    *,
    tp_id: str,
    target: str,
    series_id: str,
    allowlist: list[str],
    depends_on: list[str],
    parent_tp_id: str | None,
    final_packet: bool = False,
) -> Path:
    payload = {
        "id": tp_id,
        "project": "dopetask",
        "target": target,
        "steps": [
            {
                "id": "step_1",
                "task": f"Implement {target}",
                "validation": ["python -c 'print(\"ok\")'"],
            }
        ],
        "depends_on": depends_on,
        "series": {
            "id": series_id,
            "base_branch": "main",
            "parent_tp_id": parent_tp_id,
            "final_packet": final_packet,
        },
        "commit": {
            "message": f"{tp_id}: {target}",
            "allowlist": allowlist,
            "verify": ["git status --short"],
        },
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _fake_execute_task_packet(tp_file: Path, *, agent: str = "gemini", working_dir: Path | None = None) -> Path:
    assert working_dir is not None
    packet = json.loads(Path(tp_file).read_text(encoding="utf-8"))
    for rel_path in packet["commit"]["allowlist"]:
        file_path = working_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        content = packet["id"]
        context_path = working_dir / ".dopetask" / "SERIES_CONTEXT.json"
        if context_path.exists():
            context = json.loads(context_path.read_text(encoding="utf-8"))
            content = f"{packet['id']}:{','.join(context['depends_on'])}"
        file_path.write_text(content + "\n", encoding="utf-8")

    proof_dir = working_dir / "proof"
    proof_dir.mkdir(parents=True, exist_ok=True)
    raw_path = proof_dir / f"{packet['id']}_PROOF.json"
    raw_path.write_text(json.dumps({"tp_id": packet["id"], "steps": []}, indent=2) + "\n", encoding="utf-8")
    bundle_path = proof_dir / f"{packet['id']}_PROOF_BUNDLE.json"
    bundle_path.write_text(json.dumps({"tp_id": packet["id"], "status": "VALIDATED"}, indent=2) + "\n", encoding="utf-8")
    return bundle_path


def _fake_run_command(argv: list[str], *, cwd: Path, check: bool = True) -> ExecResult:
    rendered = " ".join(argv)
    if argv[:3] == ["gh", "auth", "status"]:
        return ExecResult(tuple(argv), cwd, 0, "logged in\n", "")
    if argv[:3] == ["gh", "pr", "create"]:
        return ExecResult(tuple(argv), cwd, 0, "https://example.test/pr/1\n", "")
    if argv[:3] == ["gh", "pr", "view"]:
        payload = json.dumps(
            {
                "url": "https://example.test/pr/1",
                "state": "OPEN",
                "mergeStateStatus": "CLEAN",
                "autoMergeRequest": None,
            }
        )
        return ExecResult(tuple(argv), cwd, 0, payload, "")
    if check:
        raise RuntimeError(f"unexpected command in test: {rendered}")
    return ExecResult(tuple(argv), cwd, 1, "", f"unexpected command: {rendered}")


def test_series_exec_supports_multiple_completed_roots_in_one_series(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    packets_dir = tmp_path / "packets"
    packets_dir.mkdir()
    packet_a = _write_packet(
        packets_dir / "tp_a.json",
        tp_id="TPA",
        target="alpha",
        series_id="SERIES-1",
        allowlist=["src/alpha.txt"],
        depends_on=[],
        parent_tp_id=None,
    )
    packet_b = _write_packet(
        packets_dir / "tp_b.json",
        tp_id="TPB",
        target="beta",
        series_id="SERIES-1",
        allowlist=["src/beta.txt"],
        depends_on=[],
        parent_tp_id=None,
    )

    monkeypatch.setattr("dopetask.ops.tp_series.logic.execute_task_packet", _fake_execute_task_packet)

    runner = CliRunner()
    monkeypatch.chdir(repo)
    result_a = runner.invoke(cli, ["tp", "series", "exec", str(packet_a), "--repo", str(repo)])
    result_b = runner.invoke(cli, ["tp", "series", "exec", str(packet_b), "--repo", str(repo)])

    assert result_a.exit_code == 0, result_a.stdout
    assert result_b.exit_code == 0, result_b.stdout

    state_path = repo / "out" / "tp_series" / "SERIES-1" / "SERIES_STATE.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert payload["packets"]["TPA"]["status"] == "completed"
    assert payload["packets"]["TPB"]["status"] == "completed"
    assert payload["packets"]["TPA"]["branch"] != payload["packets"]["TPB"]["branch"]
    assert not (repo / ".worktrees" / "TPA").exists()
    assert not (repo / ".worktrees" / "TPB").exists()


def test_series_exec_refuses_when_parent_is_not_listed_in_depends_on(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    packet = _write_packet(
        tmp_path / "invalid.json",
        tp_id="TPC",
        target="gamma",
        series_id="SERIES-2",
        allowlist=["src/gamma.txt"],
        depends_on=["TPA"],
        parent_tp_id="TPB",
    )

    runner = CliRunner()
    monkeypatch.chdir(repo)
    result = runner.invoke(cli, ["tp", "series", "exec", str(packet), "--repo", str(repo)])

    assert result.exit_code == 1
    assert "parent_tp_id must also be present in depends_on" in _output_text(result)


def test_series_exec_refuses_unmet_dependencies(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    packet = _write_packet(
        tmp_path / "needs_parent.json",
        tp_id="TPC",
        target="gamma",
        series_id="SERIES-3",
        allowlist=["src/gamma.txt"],
        depends_on=["TPA"],
        parent_tp_id="TPA",
    )

    runner = CliRunner()
    monkeypatch.chdir(repo)
    result = runner.invoke(cli, ["tp", "series", "exec", str(packet), "--repo", str(repo)])

    assert result.exit_code == 1
    assert "series dependency not found: TPA" in _output_text(result)


def test_series_finalize_requires_all_completed_packets_to_be_in_final_closure(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    packets_dir = tmp_path / "packets"
    packets_dir.mkdir()
    packet_a = _write_packet(
        packets_dir / "tp_a.json",
        tp_id="TPA",
        target="alpha",
        series_id="SERIES-4",
        allowlist=["src/alpha.txt"],
        depends_on=[],
        parent_tp_id=None,
    )
    packet_b = _write_packet(
        packets_dir / "tp_b.json",
        tp_id="TPB",
        target="beta",
        series_id="SERIES-4",
        allowlist=["src/beta.txt"],
        depends_on=[],
        parent_tp_id=None,
    )
    packet_c = _write_packet(
        packets_dir / "tp_c.json",
        tp_id="TPC",
        target="gamma",
        series_id="SERIES-4",
        allowlist=["src/gamma.txt"],
        depends_on=["TPA"],
        parent_tp_id="TPA",
        final_packet=True,
    )

    monkeypatch.setattr("dopetask.ops.tp_series.logic.execute_task_packet", _fake_execute_task_packet)

    runner = CliRunner()
    monkeypatch.chdir(repo)
    assert runner.invoke(cli, ["tp", "series", "exec", str(packet_a), "--repo", str(repo)]).exit_code == 0
    assert runner.invoke(cli, ["tp", "series", "exec", str(packet_b), "--repo", str(repo)]).exit_code == 0
    assert runner.invoke(cli, ["tp", "series", "exec", str(packet_c), "--repo", str(repo)]).exit_code == 0

    result = runner.invoke(
        cli,
        ["tp", "series", "finalize", "SERIES-4", "--repo", str(repo), "--title", "series pr"],
    )

    assert result.exit_code == 1
    assert "outside the final packet dependency closure" in _output_text(result)


def test_series_finalize_opens_single_pr_from_final_packet_branch(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    packets_dir = tmp_path / "packets"
    packets_dir.mkdir()
    packet_a = _write_packet(
        packets_dir / "tp_a.json",
        tp_id="TPA",
        target="alpha",
        series_id="SERIES-5",
        allowlist=["src/alpha.txt"],
        depends_on=[],
        parent_tp_id=None,
    )
    packet_b = _write_packet(
        packets_dir / "tp_b.json",
        tp_id="TPB",
        target="beta",
        series_id="SERIES-5",
        allowlist=["src/beta.txt"],
        depends_on=[],
        parent_tp_id=None,
    )
    packet_c = _write_packet(
        packets_dir / "tp_c.json",
        tp_id="TPC",
        target="gamma",
        series_id="SERIES-5",
        allowlist=["src/gamma.txt"],
        depends_on=["TPA", "TPB"],
        parent_tp_id="TPA",
        final_packet=True,
    )

    monkeypatch.setattr("dopetask.ops.tp_series.logic.execute_task_packet", _fake_execute_task_packet)
    monkeypatch.setattr("dopetask.ops.tp_series.logic.run_command", _fake_run_command)

    runner = CliRunner()
    monkeypatch.chdir(repo)
    assert runner.invoke(cli, ["tp", "series", "exec", str(packet_a), "--repo", str(repo)]).exit_code == 0
    assert runner.invoke(cli, ["tp", "series", "exec", str(packet_b), "--repo", str(repo)]).exit_code == 0
    assert runner.invoke(cli, ["tp", "series", "exec", str(packet_c), "--repo", str(repo)]).exit_code == 0

    result = runner.invoke(
        cli,
        ["tp", "series", "finalize", "SERIES-5", "--repo", str(repo), "--title", "series pr"],
    )

    assert result.exit_code == 0, result.stdout
    assert "url=https://example.test/pr/1" in result.stdout
    pr_payload = json.loads((repo / "out" / "tp_series" / "SERIES-5" / "SERIES_PR.json").read_text(encoding="utf-8"))
    assert pr_payload["final_tp_id"] == "TPC"
    assert pr_payload["base_branch"] == "main"
    assert pr_payload["branch"] == "tp/TPC-gamma"
