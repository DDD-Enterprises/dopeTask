import json
from datetime import datetime
from pathlib import Path
from typing import Any

class ProofWriter:
    def write(self, tp_id: str, steps: list[dict[str, Any]]) -> str:
        bundle = {
            "tp_id": tp_id,
            "timestamp": datetime.utcnow().isoformat(),
            "steps": steps
        }

        out_dir = Path("proof")
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{tp_id}_PROOF.json"

        with open(path, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)

        # Write human-readable TRACE.log
        trace_path = out_dir / f"{tp_id}_TRACE.log"
        with open(trace_path, "w", encoding="utf-8") as f:
            f.write(f"Dopetask Execution Trace - {tp_id}\n")
            f.write(f"Generated at: {datetime.utcnow().isoformat()}\n")
            f.write("=" * 60 + "\n\n")

            for step_res in steps:
                step_id = step_res.get("step_id", "UNKNOWN")
                f.write(f"STEP: {step_id}\n")
                f.write("-" * 40 + "\n")
                
                output_log = step_res.get("output_log", [])
                for entry in output_log:
                    cmd_type = entry.get("type", "exec").upper()
                    f.write(f"[{cmd_type}] Command: {entry.get('command')}\n")
                    f.write(f"Return Code: {entry.get('returncode')}\n")
                    
                    stdout = entry.get("stdout", "").strip()
                    if stdout:
                        f.write("STDOUT:\n")
                        f.write(stdout + "\n")
                    
                    stderr = entry.get("stderr", "").strip()
                    if stderr:
                        f.write("STDERR:\n")
                        f.write(stderr + "\n")
                    f.write("\n")
                
                if step_res.get("errors"):
                    f.write("ERRORS:\n")
                    for err in step_res.get("errors"):
                        f.write(f"- {err}\n")
                    f.write("\n")
                
                f.write(f"Status: {'VALIDATED' if step_res.get('validation_passed') else 'FAILED'}\n")
                f.write("\n")

        return str(path)
