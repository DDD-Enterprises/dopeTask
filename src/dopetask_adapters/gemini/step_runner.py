import json
from typing import Any

from .prompts import GEMINI_PROMPTS

class StepRunner:
    def compile_step_prompt(self, step: dict[str, Any]) -> str:
        """Compiles the TURN 3+ prompt for Gemini."""
        return GEMINI_PROMPTS["TURN_3_STEP"].format(
            step_id=step.get("id", "UNKNOWN"),
            task=step.get("task", "No task provided"),
            requirements="\n".join([f"- {req}" for req in step.get("requirements", [])]),
            validation="\n".join([f"- {val}" for val in step.get("validation", [])])
        )

    def run_step(self, step: dict[str, Any]) -> dict[str, Any]:
        prompt = self.compile_step_prompt(step)
        
        result: dict[str, Any] = {
            "step_id": step["id"],
            "files_created": [],
            "commands_run": [],
            "validation_passed": False,
            "errors": []
        }

        try:
            # TODO: Integrate actual LLM CLI execution here using `prompt`
            # For now, simulate execution and commands tracking
            for cmd in step.get("commands", []):
                result["commands_run"].append(cmd)
                # subprocess execution here

            # track files
            result["files_created"] = step.get("expected_files", [])

            # validation
            result["validation_passed"] = True

        except Exception as e:
            result["errors"].append(str(e))

        return result
