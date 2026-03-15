# PROOF BUNDLE CONTRACT

Every Task Packet (TP) in Dopetask must emit one authoritative JSON proof bundle. This bundle is the primary surface for human and automated review.

## Core Principles

1. **One TP, One Bundle**: Multi-file sprawl is replaced by a single `*_PROOF_BUNDLE.json`.
2. **Review First**: Humans, supervisors, and agents must read the bundle before any supporting evidence.
3. **Machine Readable**: The bundle follows a strict schema for automated validation and indexing.
4. **Sufficient for Signoff**: The bundle must contain enough information to justify a "Go/No-Go" decision without requiring a drill-down into archives.

## Naming Convention

The bundle must be named:
`TP-<ID>_PROOF_BUNDLE.json`

Example:
`TP-PRMS-052_PROOF_BUNDLE.json`

## Required Content

Each bundle must include:
- `tp_id`: Task identifier.
- `status`: Execution state (VALIDATED, DEFERRED, etc.).
- `summary`: Results, findings, and caveats.
- `acceptance_checks`: List of passed/failed criteria.
- `validation`: Summary of test/verification scenarios.
- `artifacts`: References to primary, supporting, and archive files.
- `manifest`: Metadata about the bundle generation.
