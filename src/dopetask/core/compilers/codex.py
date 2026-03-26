"""Codex compiler for SMART_IMPLEMENTER profile."""

from typing import Any

from dopetask.core.compilers.base import BaseCompiler
from dopetask.core.schema import TaskPacket


class CodexCompiler(BaseCompiler):
    """Compiles generic TPs into the SMART_IMPLEMENTER format for Codex.

    This profile batches steps together to provide a larger context block and
    explicitly demands full file coverage with no TODOs.
    """

    def compile(self, tp: TaskPacket) -> dict[str, Any]:
        """Compile the TaskPacket into the Codex format.

        Groups all files, requirements, and validation together into a single
        large task block.

        Args:
            tp: The generic TaskPacket instance.

        Returns:
            A dictionary containing the batched implementation request.
        """
        all_files = set()
        all_requirements = []
        all_validations = []

        for step in tp.steps:
            all_files.update(step.expected_files)
            all_requirements.extend(step.requirements)
            all_validations.extend(step.validation)

        return {
            "id": tp.id,
            "target": tp.target,
            "target_dir": "src/",  # Simplified, could be derived from files
            "files": sorted(all_files),
            "requirements": all_requirements,
            "validation": all_validations,
            "constraints": [
                "deterministic",
                "fail-closed",
                "proof bundle generation",
                "no placeholder code",
                "no TODOs",
                "no skipped files"
            ]
        }
