from __future__ import annotations

import json
from typing import Any, Optional, Literal

from dopetask.pipeline.task_runner.types import ExecutionResult

from .step_runner import StepRunner
from .proof_writer import ProofWriter
from .validator import Validator
from .prompts import GEMINI_PROMPTS

class GeminiAdapter:
    """Gemini-specific execution adapter."""

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
        self.runner = StepRunner(model=model)
        self.validator = Validator()
        self.writer = ProofWriter()

    def compile_system_prompts(self, tp: dict[str, Any]) -> tuple[str, str]:
        """Compiles TURN 1 and TURN 2 prompts for Gemini."""
        turn_1 = GEMINI_PROMPTS["TURN_1_SYSTEM_FRAME"]
        
        # Extract files from all steps
        all_files = []
        for step in tp.get("steps", []):
            all_files.extend(step.get("expected_files", []))
            
        turn_2 = GEMINI_PROMPTS["TURN_2_CONTEXT_LOAD"].format(
            project=tp.get("project", "dopetask"),
            target=tp.get("target", "Target"),
            files_to_create="\n".join([f"- {f}" for f in set(all_files)])
        )
        return turn_1, turn_2

    def run_tp(self, tp: dict[str, Any]) -> tuple[list[ExecutionResult], str]:
        """Execute a full Task Packet and return standardized results and proof path."""
        self.compile_system_prompts(tp)
        
        # TODO: Send turn_1 and turn_2 to the LLM context to initialize the session.
        
        raw_results = []
        execution_results: list[ExecutionResult] = []

        for step in tp["steps"]:
            result_dict = self.runner.run_step(step)
            raw_results.append(result_dict)
            
            # Map raw step result to ExecutionResult contract
            status: Literal["succeeded", "failed"] = "succeeded" if result_dict.get("validation_passed") else "failed"
            error = "\n".join(result_dict.get("errors", [])) if result_dict.get("errors") else None
            
            # Pack normalized fields without leaking provider internals
            normalized = {
                "files_created": result_dict.get("files_created", []),
                "commands_run": result_dict.get("commands_run", []),
                "validation_passed": result_dict.get("validation_passed", False),
                "changed_files": result_dict.get("changed_files", [])
            }
            
            exec_result = ExecutionResult(
                step_id=result_dict["step_id"],
                status=status,
                execution_mode="agent",
                raw_output=json.dumps(result_dict.get("output_log", []), indent=2),
                normalized_output=normalized,
                error=error,
            )
            execution_results.append(exec_result)

            # Enforce immediate failure on step failure
            if status == "failed":
                break

        # Write proof artifact for backward compatibility/legacy engine logic
        proof_path = self.writer.write(
            tp["id"],
            raw_results,
            metadata={
                "agent": "gemini",
                "requested_model": self.requested_model,
                "effective_model": self.model,
                "effective_model_source": self.effective_model_source,
            },
        )
        
        return execution_results, proof_path
