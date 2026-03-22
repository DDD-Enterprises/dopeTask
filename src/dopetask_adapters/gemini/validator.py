class Validator:
    def validate(self, step_result):
        if not step_result["validation_passed"]:
            raise Exception(f"Step failed: {step_result['step_id']}")

        if step_result["errors"]:
            raise Exception(f"Errors detected: {step_result['errors']}")
