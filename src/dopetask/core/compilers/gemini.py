"""Gemini compiler for STRICT_EXECUTOR profile."""

import logging
from typing import Dict, Any, List
from dopetask.core.schema import TaskPacket
from dopetask.core.compilers.base import BaseCompiler

logger = logging.getLogger(__name__)

class GeminiCompiler(BaseCompiler):
    """Compiles generic TPs into the strict, step-by-step Gemini format.
    
    This compiler enforces that all steps have explicit validation instructions.
    If a step lacks validation, the compilation fails closed to prevent Gemini 
    from hallucinating success without actual verification.
    """
    
    def compile(self, tp: TaskPacket) -> Dict[str, Any]:
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
            
        compiled_steps: List[Dict[str, Any]] = []
        
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
            })
            
        return {
            "id": tp.id,
            "project": tp.project,
            "target": tp.target,
            "steps": compiled_steps
        }
