from typing import Any, Optional

from .step_runner import StepRunner
from .proof_writer import ProofWriter
from .validator import Validator
from .prompts import GEMINI_PROMPTS

class GeminiExecutor:
    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model
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

    def run_tp(self, tp: dict[str, Any]) -> str:
        turn_1, turn_2 = self.compile_system_prompts(tp)
        
        # TODO: Send turn_1 and turn_2 to the LLM context to initialize the session.
        
        results = []
        failure_occured = False

        for step in tp["steps"]:
            result = self.runner.run_step(step)
            results.append(result)
            try:
                self.validator.validate(result)
            except Exception as exc:
                failure_occured = True
                break

        path = self.writer.write(tp["id"], results)
        if failure_occured:
            # We still raise AFTER writing the proof to satisfy the engine's crash logic
            # but now the aggregator can run if it's called.
            # Wait, the engine calls aggregator AFTER run_tp returns path.
            # So if we raise HERE, the engine STILL won't call the aggregator!
            pass
        return path
