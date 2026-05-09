"""Claude Code compiler for step-oriented task packet execution."""

from typing import Any

from dopetask.core.compilers.base import BaseCompiler
from dopetask.core.schema import TaskPacket


class ClaudeCodeCompiler(BaseCompiler):
    """Compile generic task packets into a per-step Claude Code profile."""

    def compile(self, tp: TaskPacket) -> dict[str, Any]:
        """Compile the task packet into the format expected by the Claude Code adapter."""
        if not tp.steps:
            raise ValueError("TaskPacket must have at least one step for Claude Code profile.")

        compiled_steps: list[dict[str, Any]] = []

        for index, step in enumerate(tp.steps):
            if not step.validation:
                raise ValueError(
                    f"Fail-Closed: Claude Code profile requires explicit validation. "
                    f"Step '{step.id}' (index {index}) is missing validation commands."
                )

            compiled_steps.append(
                {
                    "id": step.id,
                    "task": step.task,
                    "requirements": step.requirements,
                    "commands": step.commands,
                    "expected_files": step.expected_files,
                    "validation": step.validation,
                    "context_files": step.context_files,
                }
            )

        return {
            "id": tp.id,
            "project": tp.project,
            "target": tp.target,
            "steps": compiled_steps,
        }
