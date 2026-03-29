# Proof Archive Policy

The proof archive (`*_PROOF_ARCHIVE.zip`) is an optional, secondary container for detailed evidence, traces, and subordinate artifacts.

## Core Rules

1. **The zip is the archive container.** It is for export, storage, portability, and subordinate evidence packaging.
2. **If the TP has many supporting artifacts, one archive zip may accompany the bundle.**
3. Supporting artifacts are drill-down evidence, not the primary proof surface.
4. The zip must never be used as the canonical proof surface.

## Archive Required When

Emit `*_PROOF_ARCHIVE.zip` when the TP has any of:
- Multiple supporting JSON artifacts
- Logs
- Traces
- `.jsonl` files
- Screenshots / render snapshots
- Long validation scenario outputs
- Multiple subordinate manifests

## Archive Optional When

The TP has only:
- One bundle
- One or two tiny supporting files
- No meaningful drill-down burden

*(In such cases, the supporting files can just be placed alongside the bundle without a zip, but a bundle must still exist.)*

## Archive Contents

The archive should contain:
- All supporting artifacts for the TP.
- A small archive manifest (`PROOF_ARCHIVE_MANIFEST.json`).
- No duplicate copy of the canonical bundle unless explicitly desired for portability.

## Archive Manifest

Each zip should include a file `PROOF_ARCHIVE_MANIFEST.json` with:
- `tp_id`: The ID of the Task Packet.
- `archive_filename`: The name of the zip container.
- `generated_at`: ISO timestamp of generation.
- `included_files`: A list of objects, each containing:
  - `filename`: The name of the file within the zip (no paths).
  - `sha256`: Hash for integrity validation.
  - `description`: Text description of the artifact.
