# Canonical Proof Bundle Contract

The JSON proof bundle (`*_PROOF_BUNDLE.json`) is the canonical, primary proof surface for all Dopetask processes. It provides a standardized, machine-readable summary of a task packet's execution, validation, and final status.

## Core Rule

1. **One TP = one canonical bundle.**
2. The JSON bundle is the canonical proof surface.
3. The bundle is what humans review, supervisors cite, agents read first, and governance decisions reference.

## Bundle-First Principle

Every review flow must use this order:
1. Open `*_PROOF_BUNDLE.json`.
2. Read summary, acceptance checks, validation, and caveats.
3. Only then open supporting artifacts (if any).
4. Only then open `*_PROOF_ARCHIVE.zip` if drill-down is needed.

The zip must never become the primary review object.

## Required Top-Level Bundle Sections

Each bundle must contain at least:
- `tp_id`: The ID of the Task Packet (e.g., `TP-PRMS-052`).
- `status`: The final status (e.g., `VALIDATED`).
- `packet_family`: The family of operations (e.g., `flight_deck`).
- `lane`: The processing lane (e.g., `closed_loop`).
- `summary`: A concise summary including `result`, `key_findings`, and `key_caveats`.
- `acceptance_checks`: Lists of `passed`, `failed`, and `not_applicable` checks.
- `validation`: Summary of validation metrics and coverage notes.
- `artifacts`: References to primary and supporting artifacts, including the optional zip archive.
- `manifest`: Metadata about the bundle generation.

## Conditionally Required Sections

Required when applicable depending on the TP:
- `caveats`: Operational or contextual caveats inside the summary.
- Other extension blocks defined by specific execution adapters.

## References

- [Archive Policy](./PROOF_ARCHIVE_POLICY.md)
- [Review Guide](./BUNDLE_REVIEW_GUIDE.md)
- [Bundle Schema Detail](./DOPETASK_BUNDLE_SCHEMA.md)
