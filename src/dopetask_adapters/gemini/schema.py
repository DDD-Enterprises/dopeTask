from typing import List

class StepResult:
    def __init__(
        self,
        step_id: str,
        files_created: List[str],
        commands_run: List[str],
        validation_passed: bool,
        errors: List[str]
    ):
        self.step_id = step_id
        self.files_created = files_created
        self.commands_run = commands_run
        self.validation_passed = validation_passed
        self.errors = errors


class TPProofBundle:
    def __init__(self, tp_id: str, steps: List[StepResult]):
        self.tp_id = tp_id
        self.steps = steps
