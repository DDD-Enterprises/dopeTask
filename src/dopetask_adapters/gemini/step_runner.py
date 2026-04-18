import subprocess
from pathlib import Path
from typing import Any, Optional

from .prompts import GEMINI_PROMPTS


class StepRunner:
    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model

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
        del prompt

        expected_files = list(step.get("expected_files", []))
        before = {rel_path: Path(rel_path).exists() for rel_path in expected_files}

        result: dict[str, Any] = {
            "step_id": step["id"],
            "files_created": [],
            "commands_run": [],
            "changed_files": [],
            "validation_passed": False,
            "errors": [],
            "output_log": []  # New field for trace capture
        }

        try:
            for cmd in step.get("commands", []):
                result["commands_run"].append(cmd)
                cp = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                # Capture output for trace
                result["output_log"].append({
                    "command": cmd,
                    "stdout": cp.stdout,
                    "stderr": cp.stderr,
                    "returncode": cp.returncode,
                    "type": "execution"
                })

                if cp.returncode != 0:
                    result["errors"].append(
                        f"Command failed ({cp.returncode}): {cmd}\n"
                        f"STDOUT: {cp.stdout}\n"
                        f"STDERR: {cp.stderr}"
                    )
                    return result

            result["files_created"] = [
                rel_path
                for rel_path in expected_files
                if Path(rel_path).exists() and not before.get(rel_path, False)
            ]

            val_passed = True
            for val_cmd in step.get("validation", []):
                v_cp = subprocess.run(val_cmd, shell=True, capture_output=True, text=True)

                # Capture validation output for trace
                result["output_log"].append({
                    "command": val_cmd,
                    "stdout": v_cp.stdout,
                    "stderr": v_cp.stderr,
                    "returncode": v_cp.returncode,
                    "type": "validation"
                })

                if v_cp.returncode != 0:
                    val_passed = False
                    result["errors"].append(
                        f"Validation failed ({v_cp.returncode}): {val_cmd}\n"
                        f"STDOUT: {v_cp.stdout}\n"
                        f"STDERR: {v_cp.stderr}"
                    )
                    break
            result["validation_passed"] = val_passed

        except Exception as e:
            result["errors"].append(str(e))

        return result
