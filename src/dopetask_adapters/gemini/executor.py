from .step_runner import StepRunner
from .proof_writer import ProofWriter
from .validator import Validator

class GeminiExecutor:
    def __init__(self):
        self.runner = StepRunner()
        self.validator = Validator()
        self.writer = ProofWriter()

    def run_tp(self, tp):
        results = []

        for step in tp["steps"]:
            result = self.runner.run_step(step)
            self.validator.validate(result)
            results.append(result)

        return self.writer.write(tp["id"], results)
