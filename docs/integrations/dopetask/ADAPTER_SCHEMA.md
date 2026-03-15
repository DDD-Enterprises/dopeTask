# DOPEMUX ADAPTER SCHEMA

This is the normalized object Dopemux should use internally after loading a Dopetask proof bundle or launching a Dopetask packet.

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
    "bundle_path": "proof/bundles/TP-PRMS-050_PROOF_BUNDLE.json",
    "bundle_present": true,
    "archive_path": "proof/archives/TP-PRMS-050_PROOF_ARCHIVE.zip",
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
    "open_first": "proof/bundles/TP-PRMS-050_PROOF_BUNDLE.json",
    "open_second": "proof/archives/TP-PRMS-050_PROOF_ARCHIVE.zip",
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
