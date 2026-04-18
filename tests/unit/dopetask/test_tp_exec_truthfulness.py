"""Truthfulness coverage for raw TP proof artifacts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from dopetask.ops.tp_exec.engine import execute_task_packet


def _init_repo(path: Path) -> Path:
    path.mkdir()
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True, capture_output=True, text=True)
    (path / ".dopetaskroot").write_text("", encoding="utf-8")
    (path / ".dopetask").mkdir(parents=True, exist_ok=True)
    (path / ".dopetask" / "project.json").write_text(
        json.dumps({"project_id": "dopetask.core"}, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def test_gemini_raw_proof_does_not_claim_missing_expected_files(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    packet = repo / "packet.json"
    packet.write_text(
        json.dumps(
            {
                "id": "TP-TRUTH",
                "target": "truthful proof",
                "pal_chain": {"enabled": True, "steps": ["analysis"]},
                "steps": [
                    {
                        "id": "S1",
                        "task": "Do nothing",
                        "expected_files": ["missing.txt"],
                        "validation": ["true"],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    bundle_path = execute_task_packet(packet, agent="gemini", working_dir=repo)

    raw_proof = json.loads((repo / "proof" / "TP-TRUTH_PROOF.json").read_text(encoding="utf-8"))
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))

    assert raw_proof["steps"][0]["files_created"] == []
    assert "missing.txt" not in bundle["artifacts"]["supporting"]
