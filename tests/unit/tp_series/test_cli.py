"""Tests for DAG-aware JSON TP series execution."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

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
    (repo / ".dopetaskroot").write_text("", encoding="utf-8")
    (repo / ".dopetask").mkdir(parents=True, exist_ok=True)
    (repo / ".dopetask" / "project.json").write_text(
        json.dumps({"project_id": "dopetask.core"}, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", "README.md", ".dopetaskroot", ".dopetask/project.json")
    _git(repo, "commit", "-m", "initial")
    _git(repo, "branch", "-M", "main")
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "-u", "origin", "main")
    return repo


def _init_unborn_main_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    (repo / "README.md").write_text("# repo\n", encoding="utf-8")
    (repo / ".dopetaskroot").write_text("", encoding="utf-8")
    (repo / ".dopetask").mkdir(parents=True, exist_ok=True)
    (repo / ".dopetask" / "project.json").write_text(
        json.dumps({"project_id": "dopetask.core"}, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", "README.md", ".dopetaskroot", ".dopetask/project.json")
    _git(repo, "commit", "-m", "initial")
    return repo


def _init_local_main_repo(tmp_path: Path) -> Path:
    repo = _init_unborn_main_repo(tmp_path)
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
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
    repo_binding: dict | None = None,
    execution: dict | None = None,
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
    if repo_binding is not None:
        payload["repo_binding"] = repo_binding
    if execution is not None:
        payload["execution"] = execution
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _series_packet_payload(
    *,
    tp_id: str = "TPIMPORT",
    target: str = "imported packet",
    series_id: str = "SERIES-IMPORT",
    base_branch: str = "main",
    depends_on: list[str] | None = None,
    parent_tp_id: str | None = None,
    allowlist: list[str] | None = None,
) -> dict:
    return {
        "id": tp_id,
        "target": target,
        "steps": [
            {
                "id": "step_1",
                "task": "Validate packet",
                "validation": ["true"],
            }
        ],
        "depends_on": depends_on or [],
        "series": {
            "id": series_id,
            "base_branch": base_branch,
            "parent_tp_id": parent_tp_id,
            "final_packet": False,
        },
        "commit": {
            "message": f"{tp_id}: commit",
            "allowlist": allowlist or ["src/import.txt"],
            "verify": ["git status --short"],
        },
    }


def _fake_execute_task_packet(
    tp_file: Path,
    *,
    agent: str = "gemini",
    model: str | None = None,
    working_dir: Path | None = None,
) -> Path:
    assert working_dir is not None
    del agent, model
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


def _completed(*, args: list[str], stdout: str = "", stderr: str = "", returncode: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)


def _clipboard_run_factory(handler):
    original_run = subprocess.run

    def fake_run(argv, *args, **kwargs):
        if argv and argv[0] in {"pbpaste", "wl-paste", "xclip", "xsel"}:
            return handler(argv, *args, **kwargs)
        return original_run(argv, *args, **kwargs)

    return fake_run


def test_series_import_reads_macos_clipboard_and_writes_packet(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    payload = _series_packet_payload()

    def clipboard_run(argv: list[str], *, capture_output: bool, text: bool, check: bool):
        assert argv == ["pbpaste"]
        assert capture_output is True
        assert text is True
        assert check is False
        return _completed(args=argv, stdout=json.dumps(payload))

    monkeypatch.setattr("dopetask.ops.tp_series.logic.subprocess.run", _clipboard_run_factory(clipboard_run))
    monkeypatch.setattr("dopetask.ops.tp_series.logic.sys.platform", "darwin")
    monkeypatch.chdir(repo)

    runner = CliRunner()
    result = runner.invoke(cli, ["tp", "series", "import", "--repo", str(repo)])

    assert result.exit_code == 0, result.stdout
    packet_path = repo / "TPIMPORT.json"
    assert packet_path.exists()
    assert json.loads(packet_path.read_text(encoding="utf-8"))["id"] == "TPIMPORT"
    assert "validation=structural-ok" in result.stdout
    assert f"packet_path={packet_path}" in result.stdout
    assert f"next_command=dopetask tp series exec {packet_path} --agent gemini" in result.stdout
    assert not (repo / "out" / "tp_series" / "SERIES-IMPORT" / "SERIES_STATE.json").exists()


def test_series_import_linux_auto_falls_back_to_xclip(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    payload = _series_packet_payload(tp_id="TPLINUX")
    calls: list[list[str]] = []

    def clipboard_run(argv: list[str], *, capture_output: bool, text: bool, check: bool):
        calls.append(argv)
        if argv[0] == "wl-paste":
            raise FileNotFoundError("missing wl-paste")
        if argv[0] == "xclip":
            return _completed(args=argv, stdout=json.dumps(payload))
        raise AssertionError(f"unexpected clipboard command: {argv}")

    monkeypatch.setattr("dopetask.ops.tp_series.logic.subprocess.run", _clipboard_run_factory(clipboard_run))
    monkeypatch.setattr("dopetask.ops.tp_series.logic.sys.platform", "linux")
    monkeypatch.chdir(repo)

    runner = CliRunner()
    result = runner.invoke(cli, ["tp", "series", "import", "--repo", str(repo)])

    assert result.exit_code == 0, result.stdout
    assert calls == [["wl-paste", "--no-newline"], ["xclip", "-selection", "clipboard", "-o"]]
    assert (repo / "TPLINUX.json").exists()


def test_series_import_linux_auto_falls_back_to_xsel(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    payload = _series_packet_payload(tp_id="TPXSEL")

    def clipboard_run(argv: list[str], *, capture_output: bool, text: bool, check: bool):
        if argv[0] in {"wl-paste", "xclip"}:
            raise FileNotFoundError(f"missing {argv[0]}")
        if argv[0] == "xsel":
            return _completed(args=argv, stdout=json.dumps(payload))
        raise AssertionError(f"unexpected clipboard command: {argv}")

    monkeypatch.setattr("dopetask.ops.tp_series.logic.subprocess.run", _clipboard_run_factory(clipboard_run))
    monkeypatch.setattr("dopetask.ops.tp_series.logic.sys.platform", "linux")
    monkeypatch.chdir(repo)

    runner = CliRunner()
    result = runner.invoke(cli, ["tp", "series", "import", "--repo", str(repo)])

    assert result.exit_code == 0, result.stdout
    assert (repo / "TPXSEL.json").exists()


def test_series_import_refuses_non_strict_json_clipboard(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)

    def clipboard_run(argv: list[str], *, capture_output: bool, text: bool, check: bool):
        return _completed(args=argv, stdout="```json\n{\"id\":\"TP\"}\n```")

    monkeypatch.setattr("dopetask.ops.tp_series.logic.subprocess.run", _clipboard_run_factory(clipboard_run))
    monkeypatch.setattr("dopetask.ops.tp_series.logic.sys.platform", "darwin")
    monkeypatch.chdir(repo)

    runner = CliRunner()
    result = runner.invoke(cli, ["tp", "series", "import", "--repo", str(repo)])

    assert result.exit_code == 1
    assert "clipboard does not contain strict JSON" in _output_text(result)


def test_series_import_refuses_schema_invalid_packet(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)

    def clipboard_run(argv: list[str], *, capture_output: bool, text: bool, check: bool):
        return _completed(args=argv, stdout=json.dumps({"id": "TPBAD", "target": "missing steps"}))

    monkeypatch.setattr("dopetask.ops.tp_series.logic.subprocess.run", _clipboard_run_factory(clipboard_run))
    monkeypatch.setattr("dopetask.ops.tp_series.logic.sys.platform", "darwin")
    monkeypatch.chdir(repo)

    runner = CliRunner()
    result = runner.invoke(cli, ["tp", "series", "import", "--repo", str(repo)])

    assert result.exit_code == 1
    assert "Schema validation failed for 'task_packet'" in _output_text(result)


def test_series_import_refuses_when_series_metadata_missing(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    payload = {
        "id": "TPNO-SERIES",
        "target": "no series",
        "steps": [{"id": "step_1", "task": "run", "validation": ["true"]}],
    }

    def clipboard_run(argv: list[str], *, capture_output: bool, text: bool, check: bool):
        return _completed(args=argv, stdout=json.dumps(payload))

    monkeypatch.setattr("dopetask.ops.tp_series.logic.subprocess.run", _clipboard_run_factory(clipboard_run))
    monkeypatch.setattr("dopetask.ops.tp_series.logic.sys.platform", "darwin")
    monkeypatch.chdir(repo)

    runner = CliRunner()
    result = runner.invoke(cli, ["tp", "series", "import", "--repo", str(repo)])

    assert result.exit_code == 1
    assert "tp series import requires packet.series metadata" in _output_text(result)


def test_series_import_refuses_existing_file_without_force_and_supports_force(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    out_dir = repo / "packets"
    out_dir.mkdir()
    packet_path = out_dir / "TPFORCE.json"
    packet_path.write_text('{"stale": true}\n', encoding="utf-8")
    payload = _series_packet_payload(tp_id="TPFORCE")

    def clipboard_run(argv: list[str], *, capture_output: bool, text: bool, check: bool):
        return _completed(args=argv, stdout=json.dumps(payload))

    monkeypatch.setattr("dopetask.ops.tp_series.logic.subprocess.run", _clipboard_run_factory(clipboard_run))
    monkeypatch.setattr("dopetask.ops.tp_series.logic.sys.platform", "darwin")
    monkeypatch.chdir(repo)

    runner = CliRunner()
    refused = runner.invoke(cli, ["tp", "series", "import", "--repo", str(repo), "--out-dir", str(out_dir)])
    forced = runner.invoke(cli, ["tp", "series", "import", "--repo", str(repo), "--out-dir", str(out_dir), "--force"])

    assert refused.exit_code == 1
    assert "target file already exists" in _output_text(refused)
    assert forced.exit_code == 0, forced.stdout
    assert json.loads(packet_path.read_text(encoding="utf-8"))["id"] == "TPFORCE"


def test_series_import_refuses_when_existing_series_state_conflicts(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    payload = _series_packet_payload(tp_id="TPSTATE", series_id="SERIES-STATE", base_branch="main")
    series_dir = repo / "out" / "tp_series" / "SERIES-STATE"
    series_dir.mkdir(parents=True)
    (series_dir / "SERIES_STATE.json").write_text(
        json.dumps(
            {
                "series_id": "SERIES-STATE",
                "base_branch": "develop",
                "packets": {"TPSTATE": {"status": "completed"}},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    def clipboard_run(argv: list[str], *, capture_output: bool, text: bool, check: bool):
        return _completed(args=argv, stdout=json.dumps(payload))

    monkeypatch.setattr("dopetask.ops.tp_series.logic.subprocess.run", _clipboard_run_factory(clipboard_run))
    monkeypatch.setattr("dopetask.ops.tp_series.logic.sys.platform", "darwin")
    monkeypatch.chdir(repo)

    runner = CliRunner()
    result = runner.invoke(cli, ["tp", "series", "import", "--repo", str(repo)])

    assert result.exit_code == 1
    assert "series base branch mismatch" in _output_text(result)


def test_series_import_refuses_duplicate_packet_id_in_existing_series_state(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    payload = _series_packet_payload(tp_id="TPDUP", series_id="SERIES-DUP")
    series_dir = repo / "out" / "tp_series" / "SERIES-DUP"
    series_dir.mkdir(parents=True)
    (series_dir / "SERIES_STATE.json").write_text(
        json.dumps(
            {
                "series_id": "SERIES-DUP",
                "base_branch": "main",
                "packets": {"TPDUP": {"status": "completed"}},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    def clipboard_run(argv: list[str], *, capture_output: bool, text: bool, check: bool):
        return _completed(args=argv, stdout=json.dumps(payload))

    monkeypatch.setattr("dopetask.ops.tp_series.logic.subprocess.run", _clipboard_run_factory(clipboard_run))
    monkeypatch.setattr("dopetask.ops.tp_series.logic.sys.platform", "darwin")
    monkeypatch.chdir(repo)

    runner = CliRunner()
    result = runner.invoke(cli, ["tp", "series", "import", "--repo", str(repo)])

    assert result.exit_code == 1
    assert "packet already recorded in state: TPDUP" in _output_text(result)


def test_series_import_refuses_invalid_parent_dependency_relationship(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    payload = _series_packet_payload(
        tp_id="TPREL",
        depends_on=["TPA"],
        parent_tp_id="TPB",
    )

    def clipboard_run(argv: list[str], *, capture_output: bool, text: bool, check: bool):
        return _completed(args=argv, stdout=json.dumps(payload))

    monkeypatch.setattr("dopetask.ops.tp_series.logic.subprocess.run", _clipboard_run_factory(clipboard_run))
    monkeypatch.setattr("dopetask.ops.tp_series.logic.sys.platform", "darwin")
    monkeypatch.chdir(repo)

    runner = CliRunner()
    result = runner.invoke(cli, ["tp", "series", "import", "--repo", str(repo)])

    assert result.exit_code == 1
    assert "parent_tp_id must also be present in depends_on" in _output_text(result)


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


def test_series_exec_forwards_model_override(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    packet = _write_packet(
        tmp_path / "packet.json",
        tp_id="TPMODEL",
        target="model test",
        series_id="SERIES-MODEL",
        allowlist=["src/model.txt"],
        depends_on=[],
        parent_tp_id=None,
    )
    captured: dict[str, object] = {}

    def fake_execute(tp_file: Path, *, agent: str = "gemini", model: str | None = None, working_dir: Path | None = None) -> Path:
        captured["agent"] = agent
        captured["model"] = model
        return _fake_execute_task_packet(tp_file, agent=agent, model=model, working_dir=working_dir)

    monkeypatch.setattr("dopetask.ops.tp_series.logic.execute_task_packet", fake_execute)
    runner = CliRunner()
    monkeypatch.chdir(repo)
    result = runner.invoke(
        cli,
        ["tp", "series", "exec", str(packet), "--agent", "codex", "--model", "gpt-5.3-codex", "--repo", str(repo)],
    )

    assert result.exit_code == 0, result.stdout
    assert captured == {"agent": "codex", "model": "gpt-5.3-codex"}


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


def test_series_exec_refuses_unborn_main_without_initial_commit(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    packet = _write_packet(
        tmp_path / "packet.json",
        tp_id="TPUNBORN",
        target="unborn",
        series_id="SERIES-UNBORN",
        allowlist=["src/unborn.txt"],
        depends_on=[],
        parent_tp_id=None,
    )

    runner = CliRunner()
    monkeypatch.setattr(
        "dopetask.ops.tp_series.logic.load_repo_identity",
        lambda repo_root: SimpleNamespace(
            project_id="dopetask.core",
            project_slug=None,
            repo_remote_hint=None,
            packet_required_header=False,
        ),
    )
    monkeypatch.setattr("dopetask.ops.tp_series.logic.assert_repo_identity", lambda repo_root: None)
    monkeypatch.chdir(repo)
    result = runner.invoke(cli, ["tp", "series", "exec", str(packet), "--repo", str(repo)])

    assert result.exit_code == 1
    assert "repository has no commits yet" in _output_text(result)


def test_series_exec_supports_local_main_without_origin(tmp_path: Path, monkeypatch) -> None:
    repo = _init_local_main_repo(tmp_path)
    packet = _write_packet(
        tmp_path / "tp_local.json",
        tp_id="TPLOCAL",
        target="local root packet",
        series_id="SERIES-LOCAL",
        allowlist=["src/local.txt"],
        depends_on=[],
        parent_tp_id=None,
    )

    monkeypatch.setattr("dopetask.ops.tp_series.logic.execute_task_packet", _fake_execute_task_packet)

    runner = CliRunner()
    monkeypatch.chdir(repo)
    result = runner.invoke(cli, ["tp", "series", "exec", str(packet), "--repo", str(repo)])

    assert result.exit_code == 0, result.stdout
    state_path = repo / "out" / "tp_series" / "SERIES-LOCAL" / "SERIES_STATE.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert payload["packets"]["TPLOCAL"]["status"] == "completed"
    assert payload["packets"]["TPLOCAL"]["base_ref"] == "main"


def test_series_exec_uses_execution_branch_when_present(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo_with_origin(tmp_path)
    packet = _write_packet(
        tmp_path / "tp_branch.json",
        tp_id="TPBRANCH",
        target="branch override",
        series_id="SERIES-BRANCH",
        allowlist=["src/branch.txt"],
        depends_on=[],
        parent_tp_id=None,
        execution={
            "agent": "codex",
            "branch": "series/SERIES-BRANCH/TPBRANCH",
        },
    )

    monkeypatch.setattr("dopetask.ops.tp_series.logic.execute_task_packet", _fake_execute_task_packet)

    runner = CliRunner()
    monkeypatch.chdir(repo)
    result = runner.invoke(cli, ["tp", "series", "exec", str(packet), "--repo", str(repo), "--agent", "codex"])

    assert result.exit_code == 0, result.stdout
    state_path = repo / "out" / "tp_series" / "SERIES-BRANCH" / "SERIES_STATE.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert payload["packets"]["TPBRANCH"]["branch"] == "series/SERIES-BRANCH/TPBRANCH"


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
