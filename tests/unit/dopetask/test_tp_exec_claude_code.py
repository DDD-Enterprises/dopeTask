"""Direct task packet execution coverage for Claude Code adapter support."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from dopetask.core.tp_parser import TPNormalizer, TPParser
from dopetask.core.schema import TaskPacket, TPStep
from dopetask.ops.tp_exec.engine import execute_task_packet
from dopetask.pipeline.task_runner.types import ExecutionResult
from dopetask.schemas.validator import validate_data
from dopetask_adapters.claude_code.executor import ClaudeCodeExecutor


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


def _tp_payload(*, validation: list[str] | None = None, execution_agent: str = "claude_code") -> dict[str, object]:
    return {
        "id": "TP-CLAUDE-TEST",
        "project": "dopetask",
        "target": "claude execution",
        "execution": {
            "agent": execution_agent,
            "branch": "series/TP-CLAUDE-TEST",
        },
        "steps": [
            {
                "id": "S1",
                "task": "Create the expected file",
                "requirements": ["Use deterministic content."],
                "commands": [],
                "expected_files": ["generated.txt"],
                "validation": validation if validation is not None else ["test -f generated.txt"],
                "context_files": [],
            }
        ],
    }


def _strict_payload() -> dict[str, object]:
    payload = _tp_payload()
    payload.update(
        {
            "invariants": ["keep repo identity matched"],
            "repo_binding": {
                "project_id": "dopetask.core",
                "repo_marker": ".dopetaskroot",
                "require_identity_match": True,
            },
            "series": {
                "id": "SERIES-X",
                "base_branch": "main",
                "parent_tp_id": None,
                "final_packet": True,
            },
            "commit": {
                "message": "TP-CLAUDE-TEST: commit",
                "allowlist": ["generated.txt"],
                "verify": ["git status --short"],
            },
            "pr": {
                "title": "SERIES-X: claude packet",
                "body": "Ready for review.",
                "base": "main",
            },
        }
    )
    return payload


def _compiled_tp() -> dict[str, object]:
    return {
        "id": "TP-CLAUDE-TEST",
        "project": "dopetask",
        "target": "claude execution",
        "steps": [
            {
                "id": "S1",
                "task": "Create generated.txt",
                "requirements": ["Use deterministic content."],
                "commands": [],
                "expected_files": ["generated.txt"],
                "validation": ["test -f generated.txt", "grep -qx ok generated.txt"],
                "context_files": [],
            }
        ],
    }


def test_task_packet_schema_accepts_claude_code_without_pal_chain() -> None:
    ok, errors = validate_data(_tp_payload(), "task_packet", strict=False)

    assert ok is True
    assert errors == []


def test_strict_task_packet_schema_accepts_claude_code_without_pal_chain() -> None:
    ok, errors = validate_data(_strict_payload(), "task_packet.strict", strict=False)

    assert ok is True
    assert errors == []


def test_tp_normalizer_compiles_claude_code_without_pal_chain() -> None:
    tp = TPParser.parse_dict(_tp_payload())

    compiled = TPNormalizer.compile(tp, "claude_code")

    assert "claude_code" in TPNormalizer.COMPILERS
    assert compiled["id"] == "TP-CLAUDE-TEST"
    assert compiled["steps"][0]["validation"] == ["test -f generated.txt"]


def test_tp_normalizer_fails_closed_without_validation() -> None:
    tp = TaskPacket(
        id="TP-CLAUDE-TEST",
        target="claude execution",
        steps=[TPStep(id="S1", task="Create generated.txt", validation=[])],
    )

    with pytest.raises(ValueError, match="Claude Code profile requires explicit validation"):
        TPNormalizer.compile(tp, "claude_code")


def test_build_command_uses_verified_stdin_json_shape() -> None:
    command = ClaudeCodeExecutor()._build_command()

    assert command[:2] == ["claude", "-p"]
    assert command[command.index("--permission-mode") + 1] == "bypassPermissions"
    assert command[command.index("--output-format") + 1] == "json"
    assert "--no-session-persistence" in command
    assert command[command.index("--allowedTools") + 1] == "Bash,Write,Edit,Read"
    assert "--bare" not in command
    assert "-C" not in command
    assert "-o" not in command


def test_build_command_includes_model_when_provided() -> None:
    command = ClaudeCodeExecutor(model="claude-opus-4-5")._build_command()

    assert command[command.index("--model") + 1] == "claude-opus-4-5"


def test_build_command_refuses_bare_mode() -> None:
    with pytest.raises(RuntimeError, match="RUNNER_BARE_MODE_REFUSED"):
        ClaudeCodeExecutor(model="--bare")._build_command()


def test_claude_execution_uses_stdin_and_writes_raw_stdout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    original_run = subprocess.run
    captured: dict[str, object] = {}

    def fake_run(argv, *args, **kwargs):
        if isinstance(argv, list) and argv[:2] == ["claude", "-p"]:
            captured["argv"] = argv
            captured["args"] = args
            captured["kwargs"] = kwargs
            (repo / "generated.txt").write_text("ok\n", encoding="utf-8")
            return subprocess.CompletedProcess(argv, 0, json.dumps({"is_error": False}) + "\n", "")
        return original_run(argv, *args, **kwargs)

    monkeypatch.chdir(repo)
    monkeypatch.setattr("dopetask_adapters.claude_code.executor.subprocess.run", fake_run)
    monkeypatch.setattr(ClaudeCodeExecutor, "_detect_claude_version", lambda self: "2.1.119 (Claude Code)")

    results, proof_path = ClaudeCodeExecutor(
        model="claude-opus-4-5",
        requested_model="claude-opus-4-5",
        effective_model_source="explicit_override",
    ).run_tp(_compiled_tp())

    assert captured["args"] == ()
    assert "input" in captured["kwargs"]
    assert "Task Packet:" in captured["kwargs"]["input"]
    assert captured["kwargs"]["text"] is True
    assert captured["kwargs"]["capture_output"] is True
    assert captured["kwargs"]["check"] is False
    output_path = repo / "proof" / "TP-CLAUDE-TEST_S1_CLAUDE_OUTPUT.json"
    assert output_path.read_text(encoding="utf-8") == json.dumps({"is_error": False}) + "\n"
    assert all(isinstance(result, ExecutionResult) for result in results)
    assert results[0].execution_mode == "agent"
    assert results[0].status == "succeeded"
    assert results[0].normalized_output["files_created"] == ["generated.txt"]
    assert "generated.txt" in results[0].normalized_output["changed_files"]

    proof = json.loads(Path(proof_path).read_text(encoding="utf-8"))
    assert proof["agent"] == "claude_code"
    assert proof["prompt_delivery"] == "stdin"
    assert proof["permission_mode"] == "bypassPermissions"
    assert proof["allowed_tools"] == "Bash,Write,Edit,Read"
    assert proof["auth_mode"] == "subscription_or_oauth_likely"
    assert proof["bare_mode_used"] is False
    assert proof["claude_version"] == "2.1.119 (Claude Code)"
    execution_log = proof["steps"][0]["output_log"][0]
    assert execution_log["type"] == "execution"
    assert execution_log["parsed_json_success"] is True
    assert execution_log["prompt_delivery"] == "stdin"


@pytest.mark.parametrize(
    ("stdout", "error_code"),
    [
        ("not-json\n", "RUNNER_PARSE_FAILED"),
        ("", "RUNNER_OUTPUT_MISSING"),
        ("   \n", "RUNNER_OUTPUT_EMPTY"),
    ],
)
def test_claude_execution_fails_closed_on_bad_stdout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    stdout: str,
    error_code: str,
) -> None:
    repo = _init_repo(tmp_path / "repo")
    original_run = subprocess.run

    def fake_run(argv, *args, **kwargs):
        if isinstance(argv, list) and argv[:2] == ["claude", "-p"]:
            return subprocess.CompletedProcess(argv, 0, stdout, "")
        return original_run(argv, *args, **kwargs)

    monkeypatch.chdir(repo)
    monkeypatch.setattr("dopetask_adapters.claude_code.executor.subprocess.run", fake_run)
    monkeypatch.setattr(ClaudeCodeExecutor, "_detect_claude_version", lambda self: None)

    results, proof_path = ClaudeCodeExecutor().run_tp(_compiled_tp())

    assert results[0].status == "failed"
    assert error_code in (results[0].error or "")
    proof = json.loads(Path(proof_path).read_text(encoding="utf-8"))
    assert error_code in "\n".join(proof["steps"][0]["errors"])


def test_claude_execution_fails_closed_on_nonzero_return(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    original_run = subprocess.run

    def fake_run(argv, *args, **kwargs):
        if isinstance(argv, list) and argv[:2] == ["claude", "-p"]:
            return subprocess.CompletedProcess(argv, 2, json.dumps({"is_error": False}) + "\n", "boom\n")
        return original_run(argv, *args, **kwargs)

    monkeypatch.chdir(repo)
    monkeypatch.setattr("dopetask_adapters.claude_code.executor.subprocess.run", fake_run)
    monkeypatch.setattr(ClaudeCodeExecutor, "_detect_claude_version", lambda self: None)

    results, _proof_path = ClaudeCodeExecutor().run_tp(_compiled_tp())

    assert results[0].status == "failed"
    assert "RUNNER_EXEC_FAILED" in (results[0].error or "")


def test_claude_execution_fails_closed_on_is_error_json(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    original_run = subprocess.run

    def fake_run(argv, *args, **kwargs):
        if isinstance(argv, list) and argv[:2] == ["claude", "-p"]:
            return subprocess.CompletedProcess(argv, 0, json.dumps({"is_error": True}) + "\n", "")
        return original_run(argv, *args, **kwargs)

    monkeypatch.chdir(repo)
    monkeypatch.setattr("dopetask_adapters.claude_code.executor.subprocess.run", fake_run)
    monkeypatch.setattr(ClaudeCodeExecutor, "_detect_claude_version", lambda self: None)

    results, _proof_path = ClaudeCodeExecutor().run_tp(_compiled_tp())

    assert results[0].status == "failed"
    assert "RUNNER_EXEC_FAILED" in (results[0].error or "")


def test_claude_execution_refuses_bare_command_before_subprocess(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path / "repo")
    invoked = False

    def fake_run(argv, *args, **kwargs):
        nonlocal invoked
        if isinstance(argv, list) and argv[:2] == ["claude", "-p"]:
            invoked = True
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.chdir(repo)
    monkeypatch.setattr("dopetask_adapters.claude_code.executor.subprocess.run", fake_run)
    monkeypatch.setattr(ClaudeCodeExecutor, "_build_command", lambda self: ["claude", "-p", "--bare"])
    monkeypatch.setattr(ClaudeCodeExecutor, "_detect_claude_version", lambda self: None)

    results, _proof_path = ClaudeCodeExecutor().run_tp(_compiled_tp())

    assert invoked is False
    assert results[0].status == "failed"
    assert "RUNNER_BARE_MODE_REFUSED" in (results[0].error or "")


def test_engine_dispatches_claude_code(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    packet = repo / "packet.json"
    payload = _strict_payload()
    packet.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    captured: dict[str, object] = {}

    class FakeClaudeCodeExecutor:
        def __init__(
            self,
            model: str | None = None,
            *,
            requested_model: str | None = None,
            effective_model_source: str = "agent_default",
        ) -> None:
            captured["model"] = model
            captured["requested_model"] = requested_model
            captured["effective_model_source"] = effective_model_source

        def run_tp(self, tp: dict[str, object]) -> tuple[list[ExecutionResult], str]:
            captured["tp_id"] = tp["id"]
            proof_dir = Path("proof")
            proof_dir.mkdir(parents=True, exist_ok=True)
            proof_path = proof_dir / "TP-CLAUDE-TEST_PROOF.json"
            proof_path.write_text(
                json.dumps(
                    {
                        "tp_id": "TP-CLAUDE-TEST",
                        "steps": [
                            {
                                "step_id": "S1",
                                "files_created": [],
                                "changed_files": [],
                                "commands_run": [],
                                "validation_passed": True,
                                "errors": [],
                                "output_log": [],
                            }
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            return [
                ExecutionResult(
                    step_id="S1",
                    status="succeeded",
                    execution_mode="agent",
                    raw_output="fake claude",
                    normalized_output={
                        "files_created": [],
                        "changed_files": [],
                        "commands_run": [],
                        "validation_passed": True,
                    },
                )
            ], str(proof_path)

    monkeypatch.setattr("dopetask.ops.tp_exec.engine.ClaudeCodeExecutor", FakeClaudeCodeExecutor)

    bundle_path = execute_task_packet(packet, agent="claude_code", model="claude-opus-4-5", working_dir=repo)

    assert captured == {
        "model": "claude-opus-4-5",
        "requested_model": "claude-opus-4-5",
        "effective_model_source": "explicit_override",
        "tp_id": "TP-CLAUDE-TEST",
    }
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert bundle["status"] == "VALIDATED"
