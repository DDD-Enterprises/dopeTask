"""Claude Code-backed task packet executor."""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any, Literal, Optional

from dopetask.pipeline.task_runner.types import ExecutionResult, NormalizedOutput
from dopetask_adapters.claude_code.prompts import build_step_prompt
from dopetask_adapters.claude_code.proof_writer import ProofWriter


def _parse_status_paths(status_output: str) -> set[str]:
    changed: set[str] = set()
    items = iter(status_output.split("\0"))
    for raw_item in items:
        if not raw_item:
            continue
        status_code = raw_item[:2]
        path_fragment = raw_item[3:]
        if "R" in status_code or "C" in status_code:
            try:
                changed.add(next(items))
            except StopIteration:
                changed.add(path_fragment)
        else:
            changed.add(path_fragment)
    return changed


def _git_changed_paths(cwd: Path) -> set[str]:
    completed = subprocess.run(
        ["git", "-C", str(cwd), "status", "--porcelain", "-z", "--untracked-files=all"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return set()
    return _parse_status_paths(completed.stdout)


def _materialized_expected_files(expected_files: list[str], before: dict[str, bool]) -> list[str]:
    created: list[str] = []
    for rel_path in expected_files:
        path = Path(rel_path)
        if path.exists() and not before.get(rel_path, False):
            created.append(rel_path)
    return created


class ClaudeCodeExecutor:
    """Execute task packets one step at a time through `claude -p`."""

    def __init__(
        self,
        model: Optional[str] = None,
        *,
        requested_model: Optional[str] = None,
        effective_model_source: str = "agent_default",
    ) -> None:
        self.model = model
        self.requested_model = requested_model
        self.effective_model_source = effective_model_source
        self.permission_mode = "bypassPermissions"
        self.allowed_tools = "Bash,Write,Edit,Read"
        self.auth_mode = "subscription_or_oauth_likely"
        self.writer = ProofWriter()

    def _refuse_bare_mode(self, command: list[str]) -> None:
        if "--bare" in command:
            raise RuntimeError("RUNNER_BARE_MODE_REFUSED: Claude Code adapter never permits --bare mode.")

    def _build_command(self) -> list[str]:
        command = [
            "claude",
            "-p",
            "--permission-mode",
            self.permission_mode,
            "--output-format",
            "json",
            "--no-session-persistence",
            "--allowedTools",
            self.allowed_tools,
        ]
        if self.model:
            command.extend(["--model", self.model])
        self._refuse_bare_mode(command)
        return command

    def _detect_claude_version(self) -> Optional[str]:
        if shutil.which("claude") is None:
            return None
        try:
            completed = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
        except Exception:
            return None
        if completed.returncode != 0:
            return None
        return (completed.stdout or completed.stderr).strip() or None

    def _record_file_tracking(
        self,
        result: dict[str, Any],
        *,
        expected_files: list[str],
        before_exists: dict[str, bool],
        before_changes: set[str],
    ) -> None:
        after_changes = _git_changed_paths(Path.cwd())
        result["changed_files"] = sorted(after_changes - before_changes)
        result["files_created"] = _materialized_expected_files(expected_files, before_exists)

    def _run_local_command(self, command: str, *, result: dict[str, Any], log_type: str) -> bool:
        completed = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
        result["output_log"].append(
            {
                "command": command,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "returncode": completed.returncode,
                "type": log_type,
            }
        )
        if log_type == "command":
            result["commands_run"].append(command)
        if completed.returncode != 0:
            result["errors"].append(
                f"{log_type.title()} failed ({completed.returncode}): {command}\n"
                f"STDOUT: {completed.stdout}\n"
                f"STDERR: {completed.stderr}"
            )
            return False
        return True

    def _append_runner_error(self, result: dict[str, Any], code: str, message: str) -> None:
        result["errors"].append(f"{code}: {message}")

    def _run_step(self, tp: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
        expected_files = list(step.get("expected_files", []))
        before_exists = {rel_path: Path(rel_path).exists() for rel_path in expected_files}
        before_changes = _git_changed_paths(Path.cwd())

        proof_dir = Path("proof")
        proof_dir.mkdir(parents=True, exist_ok=True)
        step_output_path = proof_dir / f"{tp['id']}_{step['id']}_CLAUDE_OUTPUT.json"
        prompt = build_step_prompt(tp, step)

        result: dict[str, Any] = {
            "step_id": step["id"],
            "files_created": [],
            "changed_files": [],
            "commands_run": [],
            "validation_passed": False,
            "errors": [],
            "output_log": [],
        }

        try:
            command = self._build_command()
            self._refuse_bare_mode(command)
        except RuntimeError as exc:
            self._append_runner_error(result, "RUNNER_BARE_MODE_REFUSED", str(exc))
            return result

        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            check=False,
        )

        if completed.stdout != "":
            step_output_path.write_text(completed.stdout, encoding="utf-8")

        execution_log = {
            "command": shlex.join(command),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "returncode": completed.returncode,
            "type": "execution",
            "output_path": str(step_output_path),
            "prompt_delivery": "stdin",
            "permission_mode": self.permission_mode,
            "allowed_tools": self.allowed_tools,
            "parsed_json_success": False,
        }
        result["output_log"].append(execution_log)

        if completed.returncode != 0:
            self._append_runner_error(
                result,
                "RUNNER_EXEC_FAILED",
                f"Claude Code execution failed ({completed.returncode}): {shlex.join(command)}\n"
                f"STDOUT: {completed.stdout}\nSTDERR: {completed.stderr}",
            )
            self._record_file_tracking(
                result,
                expected_files=expected_files,
                before_exists=before_exists,
                before_changes=before_changes,
            )
            return result

        after_exec_changes = _git_changed_paths(Path.cwd())
        if completed.stdout == "":
            code = "RUNNER_OUTPUT_MISSING_WITH_MUTATION" if after_exec_changes - before_changes else "RUNNER_OUTPUT_MISSING"
            self._append_runner_error(result, code, "Claude Code returned success without stdout JSON.")
            self._record_file_tracking(
                result,
                expected_files=expected_files,
                before_exists=before_exists,
                before_changes=before_changes,
            )
            return result

        if not completed.stdout.strip():
            self._append_runner_error(result, "RUNNER_OUTPUT_EMPTY", "Claude Code stdout JSON was empty.")
            self._record_file_tracking(
                result,
                expected_files=expected_files,
                before_exists=before_exists,
                before_changes=before_changes,
            )
            return result

        try:
            parsed = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            self._append_runner_error(result, "RUNNER_PARSE_FAILED", f"Claude Code stdout was not valid JSON: {exc}")
            self._record_file_tracking(
                result,
                expected_files=expected_files,
                before_exists=before_exists,
                before_changes=before_changes,
            )
            return result
        execution_log["parsed_json_success"] = True

        if isinstance(parsed, dict) and parsed.get("is_error") is True:
            self._append_runner_error(result, "RUNNER_EXEC_FAILED", "Claude Code JSON reported is_error=true.")
            self._record_file_tracking(
                result,
                expected_files=expected_files,
                before_exists=before_exists,
                before_changes=before_changes,
            )
            return result

        for local_command in step.get("commands", []):
            if not self._run_local_command(local_command, result=result, log_type="command"):
                self._record_file_tracking(
                    result,
                    expected_files=expected_files,
                    before_exists=before_exists,
                    before_changes=before_changes,
                )
                return result

        for validation_command in step.get("validation", []):
            if not self._run_local_command(validation_command, result=result, log_type="validation"):
                self._record_file_tracking(
                    result,
                    expected_files=expected_files,
                    before_exists=before_exists,
                    before_changes=before_changes,
                )
                return result

        self._record_file_tracking(
            result,
            expected_files=expected_files,
            before_exists=before_exists,
            before_changes=before_changes,
        )
        result["validation_passed"] = True
        return result

    def run_tp(self, tp: dict[str, Any]) -> tuple[list[ExecutionResult], str]:
        raw_results: list[dict[str, Any]] = []
        execution_results: list[ExecutionResult] = []

        for step in tp["steps"]:
            result_dict = self._run_step(tp, step)
            raw_results.append(result_dict)

            status: Literal["succeeded", "failed"] = "succeeded" if result_dict.get("validation_passed") else "failed"
            error = "\n".join(result_dict.get("errors", [])) if result_dict.get("errors") else None
            normalized: NormalizedOutput = {
                "files_created": result_dict.get("files_created", []),
                "changed_files": result_dict.get("changed_files", []),
                "commands_run": result_dict.get("commands_run", []),
                "validation_passed": result_dict.get("validation_passed", False),
            }
            if result_dict.get("output_log"):
                command_for_output = result_dict["output_log"][0].get("command", "")
            else:
                try:
                    command_for_output = shlex.join(self._build_command())
                except RuntimeError as exc:
                    command_for_output = str(exc)
            execution_results.append(
                ExecutionResult(
                    step_id=result_dict["step_id"],
                    status=status,
                    execution_mode="agent",
                    raw_output=command_for_output,
                    normalized_output=normalized,
                    error=error,
                )
            )
            if status == "failed":
                break

        proof_path = self.writer.write(
            tp["id"],
            raw_results,
            metadata={
                "agent": "claude_code",
                "requested_model": self.requested_model,
                "effective_model": self.model,
                "effective_model_source": self.effective_model_source,
                "permission_mode": self.permission_mode,
                "allowed_tools": self.allowed_tools,
                "prompt_delivery": "stdin",
                "auth_mode": self.auth_mode,
                "bare_mode_used": False,
                "claude_version": self._detect_claude_version(),
            },
        )
        return execution_results, proof_path
