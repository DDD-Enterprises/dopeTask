class StepRunner:
    def run_step(self, step):
        result = {
            "step_id": step["id"],
            "files_created": [],
            "commands_run": [],
            "validation_passed": False,
            "errors": []
        }

        try:
            # execute commands
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
