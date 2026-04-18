"""Controlled integration coverage for the Codex tp_exec path."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from dopetask.ops.tp_exec.engine import execute_task_packet


def _init_repo(path: Path) -> Path:
    path.mkdir()
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True, capture_output=True, text=True)
    (path / ".dopetaskroot").write_text("", encoding="utf-8")
    (path / ".dopetask").mkdir(parents=True, exist_ok=True)
    (path / ".dopetask" / "project.json").write_text(
        json.dumps({"project_id": "dopetask.core"}, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def _write_fake_codex(bin_dir: Path) -> Path:
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "codex"
    script.write_text(
        """#!/usr/bin/env python3
import os
import sys
from pathlib import Path

args = sys.argv[1:]
cwd = Path.cwd()
output_path = None
if "-C" in args:
    cwd = Path(args[args.index("-C") + 1])
if "-o" in args:
    output_path = Path(args[args.index("-o") + 1])
prompt = sys.stdin.read()
mode = os.environ.get("FAKE_CODEX_MODE", "success")
if output_path is not None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("codex last message\\n", encoding="utf-8")
if mode == "success":
    (cwd / "generated.txt").write_text("hello\\n", encoding="utf-8")
elif mode == "mutate_without_output":
    if output_path is not None and output_path.exists():
        output_path.unlink()
    (cwd / "generated.txt").write_text("hello\\n", encoding="utf-8")
elif mode == "noop":
    pass
sys.stdout.write(f"fake codex ran for prompt length={len(prompt)}\\n")
sys.exit(0)
""",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def _write_packet(path: Path, *, validation: list[str], commands: list[str] | None = None) -> Path:
    payload = {
        "id": "TP-CODEX-INTEGRATION",
        "target": "integration",
        "project": "dopetask",
        "steps": [
            {
                "id": "S1",
                "task": "Create a file through codex",
                "requirements": ["Keep output deterministic."],
                "commands": commands or [],
                "expected_files": ["generated.txt"],
                "validation": validation,
                "context_files": [],
            }
        ],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def test_codex_exec_integration_success(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    fake_bin = tmp_path / "bin"
    _write_fake_codex(fake_bin)
    monkeypatch.setenv("PATH", f"{fake_bin}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_CODEX_MODE", "success")

    packet = _write_packet(
        repo / "packet.json",
        validation=["test -f generated.txt", "grep -q hello generated.txt", "test -f command.log"],
        commands=["printf 'post-codex\\n' > command.log"],
    )

    bundle_path = execute_task_packet(packet, agent="codex", model="gpt-5.3-codex", working_dir=repo)

    assert (repo / "generated.txt").read_text(encoding="utf-8") == "hello\n"
    assert (repo / "command.log").read_text(encoding="utf-8") == "post-codex\n"
    proof = json.loads((repo / "proof" / "TP-CODEX-INTEGRATION_PROOF.json").read_text(encoding="utf-8"))
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert proof["effective_model"] == "gpt-5.3-codex"
    assert proof["steps"][0]["validation_passed"] is True
    assert bundle["status"] == "VALIDATED"


def test_codex_exec_integration_fails_on_validation(monkeypatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    fake_bin = tmp_path / "bin"
    _write_fake_codex(fake_bin)
    monkeypatch.setenv("PATH", f"{fake_bin}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_CODEX_MODE", "noop")

    packet = _write_packet(repo / "packet.json", validation=["test -f generated.txt"])

    with pytest.raises(RuntimeError, match="failed one or more steps"):
        execute_task_packet(packet, agent="codex", working_dir=repo)

    proof = json.loads((repo / "proof" / "TP-CODEX-INTEGRATION_PROOF.json").read_text(encoding="utf-8"))
    assert proof["steps"][0]["validation_passed"] is False
