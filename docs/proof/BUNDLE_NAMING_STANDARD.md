# Proof Bundle Naming Standard

Consistency in filenames ensures predictability for agents and automation scripts.

## Core Naming Rules

**For any TP, the filenames must precisely follow these templates:**

- `TP-<ID>_PROOF_BUNDLE.json`
- `TP-<ID>_PROOF_ARCHIVE.zip` (if an archive is required)

## Examples

- `TP-PRMS-052_PROOF_BUNDLE.json`
- `TP-PRMS-052_PROOF_ARCHIVE.zip`

- `TP-1024_PROOF_BUNDLE.json`
- `TP-1024_PROOF_ARCHIVE.zip`

## Forbidden Practices

Humans are not to be trusted with filenames. The following are strictly forbidden:
- No alternate suffixes.
- No "final-final" suffixes.
- No "bundle_v2_REAL".
- No lowercase prefixes if the TP ID naturally uses uppercase (e.g. `tp-prms-052_PROOF_BUNDLE.json` is incorrect if the ID is `TP-PRMS-052`). Do not guess; use the exact TP ID.
- No `.tar.gz` for the standard archive; it must be `.zip`.
