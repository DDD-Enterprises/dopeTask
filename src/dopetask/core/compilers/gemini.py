"""Gemini compiler for STRICT_EXECUTOR profile."""

import logging
from typing import Any

from dopetask.core.compilers.base import BaseCompiler
from dopetask.core.schema import TaskPacket

logger = logging.getLogger(__name__)

class GeminiCompiler(BaseCompiler):
    """Compiles generic TPs into the strict, step-by-step Gemini format.

    This compiler enforces that all steps have explicit validation instructions.
    If a step lacks validation, the compilation fails closed to prevent Gemini
    from hallucinating success without actual verification.
    """

    def compile(self, tp: TaskPacket) -> dict[str, Any]:
        """Compile the TaskPacket into the format expected by GeminiExecutor.

        Args:
            tp: The generic TaskPacket instance.

        Returns:
            A dictionary formatted for the Gemini adapter.

        Raises:
            ValueError: If any step lacks validation commands or requirements.
        """
        if not tp.steps:
            raise ValueError("TaskPacket must have at least one step for Gemini profile.")
        pal_chain = tp.pal_chain
        if not pal_chain or not pal_chain.enabled:
            raise ValueError("Fail-Closed: Gemini execution requires a valid and enabled pal_chain block.")
        if not pal_chain.steps:
            raise ValueError("Fail-Closed: Gemini execution requires non-empty pal_chain.steps.")
        if len(pal_chain.steps) < len(tp.steps):
            raise ValueError(
                f"Fail-Closed: Each execution step must have a corresponding PAL step mapping (found {len(pal_chain.steps)} PAL steps for {len(tp.steps)} TP steps)."
            )

        compiled_steps: list[dict[str, Any]] = []

        for index, step in enumerate(tp.steps):
            # Gemini-specific failure rail: Validation is STRICTLY REQUIRED
            if not step.validation:
                raise ValueError(
                    f"Fail-Closed: Gemini profile requires explicit validation. "
                    f"Step '{step.id}' (index {index}) is missing validation commands."
                )

            compiled_steps.append({
                "id": step.id,
                "task": step.task,
                "requirements": step.requirements,
                "commands": step.commands,
                "expected_files": step.expected_files,
                "validation": step.validation,
                "context_files": step.context_files,
            })

        return {
            "id": tp.id,
            "project": tp.project,
            "target": tp.target,
            "steps": compiled_steps,
        }
