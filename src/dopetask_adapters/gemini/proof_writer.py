import json
from datetime import datetime

class ProofWriter:
    def write(self, tp_id, steps):
        bundle = {
            "tp_id": tp_id,
            "timestamp": datetime.utcnow().isoformat(),
            "steps": steps
        }

        path = f"proof/{tp_id}_PROOF.json"

        with open(path, "w") as f:
            json.dump(bundle, f, indent=2)

        return path
