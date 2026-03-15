# BUNDLE NAMING STANDARD

Consistency in naming is required for automated indexing and reliable human navigation.

## Primary Artifacts

| Type | Pattern | Example |
| --- | --- | --- |
| Proof Bundle | `TP-<ID>_PROOF_BUNDLE.json` | `TP-PRMS-052_PROOF_BUNDLE.json` |
| Proof Archive | `TP-<ID>_PROOF_ARCHIVE.zip` | `TP-PRMS-052_PROOF_ARCHIVE.zip` |
| Archive Manifest | `PROOF_ARCHIVE_MANIFEST.json` | (Always inside the zip) |

## Standard IDs

- Use uppercase `TP` prefix.
- Use hyphens for separators.
- Preserve leading zeros for numerical IDs (e.g., `052`).

## Forbidden Patterns

- **No Date Suffixes**: Use the `manifest.generated_at` field inside the JSON instead.
- **No Version Suffixes**: (e.g., `_v2`, `_final`).
- **No Descriptive Suffixes**: Keys in the bundle summary should handle descriptions.
- **No spaces**: Use hyphens or underscores as defined above.
