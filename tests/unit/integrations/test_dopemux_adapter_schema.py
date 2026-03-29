"""Schema checks for the Dopemux adapter envelope."""

import json
from pathlib import Path

from jsonschema import validate

from dopetask.utils.schema_registry import SchemaRegistry


def _example_payload() -> dict:
    return {
        "source": "dopetask",
        "schema_version": "1.0",
        "tp": {
            "id": "TP-PRMS-050",
            "family": "flight_deck",
            "lane": "ops",
            "title": "FLIGHT-DECK-OPERATIONALIZATION",
            "status": "OPERATIONAL",
            "run_id": "2026-03-14T19-22-11Z",
        },
        "target": {
            "repo": "dopemux-mvp",
            "worktree": "/Users/hue/code/dopemux-mvp",
            "ref": "main",
            "pr_number": 123,
            "case_id": "fd-ops-000123",
        },
        "posture": {
            "mode": "GO_SUPERVISED_ONLY",
            "advisory_only": False,
            "signoff_required": True,
            "defer_only": False,
            "auto_apply_allowed": True,
            "auto_apply_risk_threshold": "LOW",
        },
        "summary": {
            "result": "Flight deck operationalized under supervised posture",
            "next_action": "Continue supervised operations monitoring",
            "headline_state": "SUPERVISED",
            "confidence": "HIGH",
            "risk": "MEDIUM",
            "key_findings": [
                "Operator signoff logging enabled",
                "Auto-apply guardrails active",
            ],
            "key_caveats": [
                "Do not lower LOW auto-apply threshold without further data",
            ],
        },
        "proof": {
            "bundle_path": "proof/TP-PRMS-050_PROOF_BUNDLE.json",
            "bundle_present": True,
            "archive_path": "proof/TP-PRMS-050_PROOF_ARCHIVE.zip",
            "archive_present": True,
            "supporting_artifacts": [
                "proof/pr_merge/flight_deck/ops/OPERATIONALIZATION_REPORT.json",
                "proof/pr_merge/flight_deck/ops/ALLOWED_ACTIONS_STATE.json",
            ],
        },
        "governance": {
            "allowed_actions": [
                "MISSION_SUMMARY",
                "TACTICAL_RECOMMENDATION",
                "LOW_RISK_AUTO_APPLY",
                "GATING_REFRESH",
            ],
            "blocked_actions": [
                "MEDIUM_RISK_AUTO_APPLY",
                "HIGH_RISK_AUTO_APPLY",
                "UNSUPERVISED_SYNTH_PATCH",
            ],
            "signoff": {
                "required": True,
                "owner": "human_integrator",
                "reason": "Supervised posture requires explicit review for synthesized patch paths",
            },
        },
        "operator_view": {
            "open_first": "proof/TP-PRMS-050_PROOF_BUNDLE.json",
            "open_second": "proof/TP-PRMS-050_PROOF_ARCHIVE.zip",
            "recommended_panel": "mission_header",
            "artifact_priority": [
                "bundle",
                "ops_report",
                "allowed_actions_state",
                "archive",
            ],
        },
        "integration": {
            "loaded_from": "bundle",
            "adapter_status": "READY",
            "errors": [],
            "warnings": [],
        },
    }


def test_schema_registry_loads_dopemux_adapter_envelope() -> None:
    registry = SchemaRegistry()
    schema = registry.get_json("dopemux_adapter_envelope")
    assert schema["title"] == "Dopemux Adapter Envelope Schema"


def test_example_payload_validates_against_schema() -> None:
    registry = SchemaRegistry()
    schema = registry.get_json("dopemux_adapter_envelope")
    validate(instance=_example_payload(), schema=schema)


def test_repo_and_packaged_schema_match() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    source_schema = json.loads(
        (repo_root / "schemas" / "dopemux_adapter_envelope.schema.json").read_text(encoding="utf-8")
    )
    packaged_schema = json.loads(
        (repo_root / "dopetask_schemas" / "dopemux_adapter_envelope.schema.json").read_text(encoding="utf-8")
    )
    assert source_schema == packaged_schema
