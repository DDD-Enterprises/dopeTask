import json
from datetime import datetime
from typing import Any

class ProofWriter:
    def write(self, tp_id: str, steps: list[dict[str, Any]]) -> str:
        bundle = {
            "tp_id": tp_id,
            "timestamp": datetime.utcnow().isoformat(),
            "steps": steps
        }

        path = f"proof/{tp_id}_PROOF.json"

        with open(path, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)

        return path
