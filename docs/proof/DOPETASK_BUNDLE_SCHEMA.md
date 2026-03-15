# DOPETASK BUNDLE SCHEMA

The Proof Bundle is a structured JSON document that provides a high-level summary of a Task Packet's execution and validation.

## JSON Structure

```json
{
  "tp_id": "STRING",
  "status": "VALIDATED | DEFERRED | FAILED | PARTIAL",
  "packet_family": "STRING (e.g., flight_deck, pr_prep)",
  "lane": "STRING (e.g., closed_loop, assisted)",
  "summary": {
    "result": "STRING",
    "key_findings": ["STRING"],
    "key_caveats": ["STRING"]
  },
  "acceptance_checks": {
    "passed": ["STRING"],
    "failed": ["STRING"],
    "not_applicable": ["STRING"]
  },
  "validation": {
    "scenario_count": "INTEGER",
    "scenario_summary": ["STRING"],
    "coverage_notes": ["STRING"]
  },
  "decision": {
    "value": "ANY",
    "confidence": "HIGH | MEDIUM | LOW | INSUFFICIENT",
    "rationale": ["STRING"]
  },
  "artifacts": {
    "primary": ["STRING (paths)"],
    "supporting": ["STRING (paths)"],
    "archive": {
      "present": "BOOLEAN",
      "filename": "STRING",
      "sha256": "STRING"
    }
  },
  "dopetask": {
    "canonical_review_surface": true,
    "supporting_artifacts_retained": "BOOLEAN",
    "source_manifest": "STRING (optional)"
  },
  "manifest": {
    "generated_at": "ISO8601 TIMESTAMP",
    "bundle_schema_version": "1.0"
  }
}
```

## Field Definitions

- `summary.key_findings`: Strategic outcomes of the task.
- `acceptance_checks`: Direct mapping to the packet's acceptance criteria.
- `decision.value`: The core outcome (e.g., GO_DRAFT_FIRST).
- `artifacts.archive`: Metadata for the accompanying ZIP file.
