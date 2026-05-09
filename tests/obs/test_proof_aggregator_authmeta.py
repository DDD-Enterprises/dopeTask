"""Auth metadata coverage for canonical proof bundle aggregation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from dopetask.obs.proof_aggregator import ProofAggregator


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact(tmp_path: Path) -> Path:
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("evidence\n", encoding="utf-8")
    return artifact


def _execution_result(**metadata: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "steps": [
            {
                "step_id": "S1",
                "validation_passed": True,
            }
        ],
        "packet_family": "test_family",
        "lane": "agent_exec",
    }
    payload.update(metadata)
    return payload


def test_proof_bundle_schema_validates_without_runtime_metadata(tmp_path: Path) -> None:
    schema = _load_json(REPO_ROOT / "proof" / "standards" / "PROOF_BUNDLE_SCHEMA.json")
    bundle_path = ProofAggregator("TP-AUTHMETA-NONE", output_dir=tmp_path).aggregate(
        _execution_result(),
        [_artifact(tmp_path)],
    )
    bundle = _load_json(bundle_path)

    validate(bundle, schema)
    assert "runtime" not in bundle


def test_proof_bundle_schema_validates_with_runtime_auth_metadata(tmp_path: Path) -> None:
    schema = _load_json(REPO_ROOT / "proof" / "standards" / "PROOF_BUNDLE_SCHEMA.json")
    bundle_path = ProofAggregator("TP-AUTHMETA-RUNTIME", output_dir=tmp_path).aggregate(
        _execution_result(
            auth_mode="subscription_or_oauth_likely",
            bare_mode_used=False,
            permission_mode="bypassPermissions",
            allowed_tools="Bash,Write,Edit,Read",
            requested_model="claude-opus-4-5",
            effective_model="claude-opus-4-5",
            effective_model_source="explicit_override",
        ),
        [_artifact(tmp_path)],
    )
    bundle = _load_json(bundle_path)

    validate(bundle, schema)
    assert bundle["runtime"] == {
        "auth_mode": "subscription_or_oauth_likely",
        "bare_mode_used": False,
        "permission_mode": "bypassPermissions",
        "allowed_tools": "Bash,Write,Edit,Read",
        "requested_model": "claude-opus-4-5",
        "effective_model": "claude-opus-4-5",
        "effective_model_source": "explicit_override",
    }


def test_proof_bundle_runtime_auth_defaults_to_unknown_not_subscription(tmp_path: Path) -> None:
    bundle_path = ProofAggregator("TP-AUTHMETA-UNKNOWN", output_dir=tmp_path).aggregate(
        _execution_result(
            requested_model=None,
            effective_model=None,
            effective_model_source="agent_default",
        ),
        [_artifact(tmp_path)],
    )
    bundle = _load_json(bundle_path)

    assert bundle["runtime"]["auth_mode"] == "unknown"
    assert bundle["runtime"]["auth_mode"] != "subscription"
