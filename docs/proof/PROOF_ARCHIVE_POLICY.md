# PROOF ARCHIVE POLICY

While the JSON bundle is the primary review surface, supporting evidence (logs, traces, snapshots) should be consolidated into a ZIP archive to maintain repository cleanliness.

## When an Archive is Required

Emit `TP-<ID>_PROOF_ARCHIVE.zip` if any of the following exist:
- Multiple supporting JSON artifacts.
- Execution logs or traces.
- Large validation scenario outputs.
- Subordinate manifests.
- Rendered screenshots or snapshots.

## When an Archive is Optional

A ZIP archive is optional if:
- Only the JSON bundle is required.
- Supporting evidence consists of one or two trivial files that do not justify packaging.

## Archive Structure

1. **Naming**: `TP-<ID>_PROOF_ARCHIVE.zip`.
2. **Manifest**: Must contain `PROOF_ARCHIVE_MANIFEST.json` at the root.
3. **No Duplication**: The canonical JSON bundle should *not* be inside the zip unless specifically requested for external portability.

## Review Flow

Archives are for **drill-down** and **forensics** only. They must not be the primary target for initial review.
