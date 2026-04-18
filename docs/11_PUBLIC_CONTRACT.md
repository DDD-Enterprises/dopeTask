# Public Contract

This document defines dopeTask's public, user-visible contract: inputs, outputs, determinism, exit codes, and non-goals.
JSON Task Packet series (tp series) is the authoritative and default operator workflow path. Other planes are available for specialist or reference usage.
`tp series` is the default operator workflow; route/orchestrate remains an active public contract surface.

## Inputs

Default operator workflow inputs:

- JSON Task Packet for `tp series`: see `13_TASK_PACKET_FORMAT.md`

Active non-default public inputs:

- JSON Task Packet for low-level `tp exec`: see `13_TASK_PACKET_FORMAT.md`
- Route availability config for route/orchestrate surfaces: `.dopetask/runtime/availability.yaml`

## Outputs

dopeTask writes deterministic artifacts for a given invocation:

Default operator workflow outputs include canonical proof bundles and the SERIES_STATE.json ledger.

Active non-default public outputs include:

- low-level proof artifacts under `proof/` for `tp exec`
- Route plan artifacts under `out/dopetask_route/`
- Refusal reasons when refusing

Console output is informational. Artifacts are the record.

Agent/runtime parity is not universal across planes:

- `tp exec` currently supports `gemini` and `codex`
- route/orchestrate remains a separate runner plane with its own contracts

## Determinism rules

For identical:

- Packet
- Declared inputs
- dopeTask version

Outputs must be byte-stable unless explicitly documented otherwise.

## Exit codes

- `0`: success
- `2`: refusal (contractual non-execution)
- `1`: error (unexpected failure)

## Non-goals

- Implicit retries and fallback runners
- Undeclared network access
- Cross-run mutable state

## Versioning policy

dopeTask follows Semantic Versioning.

- Patch: bug fixes only
- Minor: additive and backward-compatible
- Major: contract-breaking
