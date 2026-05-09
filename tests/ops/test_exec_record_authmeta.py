"""Auth metadata coverage for TP series EXEC.json records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from dopetask.ops.tp_series.logic import _exec_runtime_metadata, _read_proof_metadata


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_exec_runtime_metadata_defaults_missing_auth_to_unknown() -> None:
    metadata = _exec_runtime_metadata({})

    assert metadata == {
        "auth_mode": "unknown",
        "bare_mode_used": None,
        "permission_mode": None,
        "allowed_tools": None,
    }
    assert metadata["auth_mode"] != "subscription"


def test_read_proof_metadata_preserves_auth_fields(tmp_path: Path) -> None:
    proof_dir = tmp_path / "run"
    proof_dir.mkdir()
    proof_path = proof_dir / "TP-AUTHMETA_PROOF.json"
    proof_path.write_text(
        json.dumps(
            {
                "tp_id": "TP-AUTHMETA",
                "requested_model": "claude-opus-4-5",
                "effective_model": "claude-opus-4-5",
                "effective_model_source": "explicit_override",
                "auth_mode": "subscription_or_oauth_likely",
                "bare_mode_used": False,
                "permission_mode": "bypassPermissions",
                "allowed_tools": "Bash,Write,Edit,Read",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    metadata = _read_proof_metadata(run_dir=proof_dir, tp_id="TP-AUTHMETA")

    assert metadata == {
        "auth_mode": "subscription_or_oauth_likely",
        "bare_mode_used": False,
        "permission_mode": "bypassPermissions",
        "allowed_tools": "Bash,Write,Edit,Read",
        "requested_model": "claude-opus-4-5",
        "effective_model": "claude-opus-4-5",
        "effective_model_source": "explicit_override",
    }


def test_exec_record_schema_accepts_additive_auth_metadata() -> None:
    schema = _load_json(REPO_ROOT / "dopetask_schemas" / "exec_record.schema.json")
    payload = {
        "schema_version": "1.0",
        "series_id": "SERIES-AUTHMETA",
        "tp_id": "TP-AUTHMETA",
        "branch": "codex/authmeta",
        "base_ref": "main",
        "packet_path": "/tmp/packet.json",
        "bundle_path": "/tmp/proof/TP-AUTHMETA_PROOF_BUNDLE.json",
        "copied_proof_bundle": None,
        "agent": "claude_code",
        "model": "claude-opus-4-5",
        "requested_model": "claude-opus-4-5",
        "effective_model": "claude-opus-4-5",
        "effective_model_source": "explicit_override",
        "auth_mode": "subscription_or_oauth_likely",
        "bare_mode_used": False,
        "permission_mode": "bypassPermissions",
        "allowed_tools": "Bash,Write,Edit,Read",
        "verify": [],
        "committed_files": ["README.md"],
        "context": {
            "schema_version": "1.0",
            "series_id": "SERIES-AUTHMETA",
            "tp_id": "TP-AUTHMETA",
            "parent_tp_id": None,
            "depends_on": [],
            "dependencies": {},
        },
        "head_sha": "a" * 40,
    }

    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda error: list(error.path))

    assert errors == []


def test_exec_record_schema_still_accepts_historical_fixture_without_authmeta() -> None:
    schema = _load_json(REPO_ROOT / "dopetask_schemas" / "exec_record.schema.json")
    fixture = _load_json(
        REPO_ROOT
        / "out"
        / "tp_series"
        / "SERIES-AUDIT-057F-PROMPT-PIPELINE"
        / "packets"
        / "TP-AUDIT-057F-PROMPT-PIPELINE"
        / "EXEC.json"
    )

    errors = sorted(Draft202012Validator(schema).iter_errors(fixture), key=lambda error: list(error.path))

    assert errors == []
