"""Codex-backed task packet executor."""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any, Optional

from dopetask.pipeline.task_runner.types import ExecutionResult
from dopetask_adapters.codex.proof_writer import ProofWriter
from dopetask_adapters.codex.prompts import build_step_prompt


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


class CodexExecutor:
    """Execute task packets one step at a time through `codex exec`."""

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
        self.writer = ProofWriter()

    def _build_command(self, *, output_path: Path) -> list[str]:
        command = [
            "codex",
            "exec",
            "--skip-git-repo-check",
            "--sandbox",
            "workspace-write",
            "-C",
            str(Path.cwd()),
            "-o",
            str(output_path),
            "-",
        ]
        if self.model:
            command[2:2] = ["--model", self.model]
        return command

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

    def _run_step(self, tp: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
        expected_files = list(step.get("expected_files", []))
        before_exists = {rel_path: Path(rel_path).exists() for rel_path in expected_files}
        before_changes = _git_changed_paths(Path.cwd())

        proof_dir = Path("proof")
        proof_dir.mkdir(parents=True, exist_ok=True)
        step_output_path = proof_dir / f"{tp['id']}_{step['id']}_CODEX_OUTPUT.txt"
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

        command = self._build_command(output_path=step_output_path)
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            check=False,
        )
        result["output_log"].append(
            {
                "command": shlex.join(command),
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "returncode": completed.returncode,
                "type": "execution",
                "output_path": str(step_output_path),
            }
        )

        if completed.returncode != 0:
            result["errors"].append(
                f"Codex execution failed ({completed.returncode}): {shlex.join(command)}\n"
                f"STDOUT: {completed.stdout}\n"
                f"STDERR: {completed.stderr}"
            )
            return result

        after_exec_changes = _git_changed_paths(Path.cwd())
        if not step_output_path.exists():
            reason = (
                "Codex reported success but the required output artifact was not written."
                if not (after_exec_changes - before_changes)
                else "Codex reported success but did not write the required output artifact after mutating the repo."
            )
            result["errors"].append(reason)
            return result

        if not step_output_path.read_text(encoding="utf-8").strip():
            reason = (
                "Codex output artifact was empty."
                if not (after_exec_changes - before_changes)
                else "Codex output artifact was empty after mutating the repo."
            )
            result["errors"].append(reason)
            return result

        for local_command in step.get("commands", []):
            if not self._run_local_command(local_command, result=result, log_type="command"):
                return result

        after_commands_changes = _git_changed_paths(Path.cwd())
        result["changed_files"] = sorted(after_commands_changes - before_changes)
        result["files_created"] = _materialized_expected_files(expected_files, before_exists)

        for validation_command in step.get("validation", []):
            if not self._run_local_command(validation_command, result=result, log_type="validation"):
                return result

        result["validation_passed"] = True
        return result

    def run_tp(self, tp: dict[str, Any]) -> tuple[list[ExecutionResult], str]:
        raw_results: list[dict[str, Any]] = []
        execution_results: list[ExecutionResult] = []

        for step in tp["steps"]:
            result_dict = self._run_step(tp, step)
            raw_results.append(result_dict)

            status = "succeeded" if result_dict.get("validation_passed") else "failed"
            error = "\n".join(result_dict.get("errors", [])) if result_dict.get("errors") else None
            normalized = {
                "files_created": result_dict.get("files_created", []),
                "changed_files": result_dict.get("changed_files", []),
                "commands_run": result_dict.get("commands_run", []),
                "validation_passed": result_dict.get("validation_passed", False),
            }
            execution_results.append(
                ExecutionResult(
                    step_id=result_dict["step_id"],
                    status=status,
                    execution_mode="agent",
                    raw_output=shlex.join(self._build_command(output_path=Path("proof") / f"{tp['id']}_{step['id']}_CODEX_OUTPUT.txt")),
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
                "agent": "codex",
                "requested_model": self.requested_model,
                "effective_model": self.model,
                "effective_model_source": self.effective_model_source,
            },
        )
        return execution_results, proof_path
