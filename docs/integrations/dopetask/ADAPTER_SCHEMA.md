# DOPEMUX ADAPTER SCHEMA

This is the normalized integration envelope Dopemux can use internally after reading canonical dopeTask artifacts.

It is a derived integration object, not a canonical artifact emitted by dopeTask itself.

## Canonical inputs

Build this envelope from the canonical sources below:

- `proof/<TP_ID>_PROOF_BUNDLE.json`
- `out/tp_series/<series-id>/SERIES_STATE.json`
- `out/tp_series/<series-id>/SERIES_PR.json` after finalization
- any Dopemux-local governance metadata you add above those sources

The JSON schema for this envelope lives in:

- `schemas/dopemux_adapter_envelope.schema.json`
- `dopetask_schemas/dopemux_adapter_envelope.schema.json`

## Canonical Normalized Object

```json
{
  "source": "dopetask",
  "schema_version": "1.0",
  "tp": {
    "id": "TP-PRMS-050",
    "family": "flight_deck",
    "lane": "ops",
    "title": "FLIGHT-DECK-OPERATIONALIZATION",
    "status": "OPERATIONAL",
    "run_id": "2026-03-14T19-22-11Z"
  },
  "target": {
    "repo": "dopemux-mvp",
    "worktree": "/Users/hue/code/dopemux-mvp",
    "ref": "main",
    "pr_number": 123,
    "case_id": "fd-ops-000123"
  },
  "posture": {
    "mode": "GO_SUPERVISED_ONLY",
    "advisory_only": false,
    "signoff_required": true,
    "defer_only": false,
    "auto_apply_allowed": true,
    "auto_apply_risk_threshold": "LOW"
  },
  "summary": {
    "result": "Flight deck operationalized under supervised posture",
    "next_action": "Continue supervised operations monitoring",
    "headline_state": "SUPERVISED",
    "confidence": "HIGH",
    "risk": "MEDIUM",
    "key_findings": [
      "Operator signoff logging enabled",
      "Auto-apply guardrails active"
    ],
    "key_caveats": [
      "Do not lower LOW auto-apply threshold without further data"
    ]
  },
  "proof": {
    "bundle_path": "proof/TP-PRMS-050_PROOF_BUNDLE.json",
    "bundle_present": true,
    "archive_path": "proof/TP-PRMS-050_PROOF_ARCHIVE.zip",
    "archive_present": true,
    "supporting_artifacts": [
      "proof/pr_merge/flight_deck/ops/OPERATIONALIZATION_REPORT.json",
      "proof/pr_merge/flight_deck/ops/ALLOWED_ACTIONS_STATE.json"
    ]
  },
  "governance": {
    "allowed_actions": [
      "MISSION_SUMMARY",
      "TACTICAL_RECOMMENDATION",
      "LOW_RISK_AUTO_APPLY",
      "GATING_REFRESH"
    ],
    "blocked_actions": [
      "MEDIUM_RISK_AUTO_APPLY",
      "HIGH_RISK_AUTO_APPLY",
      "UNSUPERVISED_SYNTH_PATCH"
    ],
    "signoff": {
      "required": true,
      "owner": "human_integrator",
      "reason": "Supervised posture requires explicit review for synthesized patch paths"
    }
  },
  "operator_view": {
    "open_first": "proof/TP-PRMS-050_PROOF_BUNDLE.json",
    "open_second": "proof/TP-PRMS-050_PROOF_ARCHIVE.zip",
    "recommended_panel": "mission_header",
    "artifact_priority": [
      "bundle",
      "ops_report",
      "allowed_actions_state",
      "archive"
    ]
  },
  "integration": {
    "loaded_from": "bundle",
    "adapter_status": "READY",
    "errors": [],
    "warnings": []
  }
}
```

## Status Values

- **tp.status**: PLANNED, IN_PROGRESS, VALIDATED, OPERATIONAL, BLOCKED, DEFERRED, FAILED, UNKNOWN.
- **posture.mode**: ADVISORY_ONLY, GO_SUPERVISED_ONLY, LIVE_SAFE, DEFER_ONLY, UNKNOWN.
- **summary.headline_state**: READY, BLOCKED, DEFERRED, SUPERVISED, INCIDENT, UNKNOWN.

## Contract notes

- `proof.bundle_path` and `proof.archive_path` should point to canonical dopeTask artifacts, not to historical fixture folders.
- `target.pr_number` may be `null` until the series is finalized.
- `target.case_id` may be `null` if Dopemux has not assigned a case yet.
- `integration.errors` and `integration.warnings` are integration-side status arrays and are not produced by dopeTask proof generation.
