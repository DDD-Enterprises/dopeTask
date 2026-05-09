"""Claude Code proof writer auth metadata pass-through tests."""

from __future__ import annotations

import json
from pathlib import Path

from dopetask_adapters.claude_code.proof_writer import ProofWriter


def test_claude_proof_writer_preserves_runtime_auth_metadata(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    proof_path = ProofWriter().write(
        "TP-CLAUDE-AUTHMETA",
        [
            {
                "step_id": "S1",
                "validation_passed": True,
                "output_log": [],
                "errors": [],
            }
        ],
        metadata={
            "agent": "claude_code",
            "auth_mode": "subscription_or_oauth_likely",
            "bare_mode_used": False,
            "permission_mode": "bypassPermissions",
            "allowed_tools": "Bash,Write,Edit,Read",
            "requested_model": "claude-opus-4-5",
            "effective_model": "claude-opus-4-5",
            "effective_model_source": "explicit_override",
        },
    )

    proof = json.loads(Path(proof_path).read_text(encoding="utf-8"))

    assert proof["auth_mode"] == "subscription_or_oauth_likely"
    assert proof["bare_mode_used"] is False
    assert proof["permission_mode"] == "bypassPermissions"
    assert proof["allowed_tools"] == "Bash,Write,Edit,Read"
    assert proof["effective_model_source"] == "explicit_override"
