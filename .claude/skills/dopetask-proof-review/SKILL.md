# dopeTask Proof Review

Use this skill when reviewing a completed dopeTask packet or series packet.

## Review order

1. Open `*_PROOF_BUNDLE.json`
2. Read:
   - `status`
   - `summary`
   - `acceptance_checks`
   - `validation`
   - caveats
3. Identify the first hard failure or first ambiguous gap
4. Inspect supporting artifacts only if required
5. Inspect the archive only if the bundle is insufficient for diagnosis

## Output contract

Return one of:

- `SUCCESS_CONFIRMED`
- `CORRECTIVE_PACKET_REQUIRED`
- `BUNDLE_DEFICIENT`
