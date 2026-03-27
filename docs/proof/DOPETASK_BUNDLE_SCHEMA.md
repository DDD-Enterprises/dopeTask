# Dopetask Bundle Schema Documentation

This document describes the technical structure of the canonical `PROOF_BUNDLE_SCHEMA.json` and its fields.

## Schema Overview

The JSON bundle uses a strictly defined JSON Schema (`proof/standards/PROOF_BUNDLE_SCHEMA.json`). 
All standard proof bundles must validate against this schema.

## Root Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tp_id` | `string` | Yes | The Task Packet ID (e.g., `TP-PRMS-052`). |
| `status` | `string` | Yes | The final state of the packet (e.g., `VALIDATED`, `FAILED`, `PENDING`). |
| `packet_family` | `string` | Yes | The broader category of the packet (e.g., `flight_deck`, `control_plane`). |
| `lane` | `string` | Yes | The execution lane (e.g., `closed_loop`). |
| `summary` | `object` | Yes | High-level summary of the execution outcome. |
| `acceptance_checks` | `object` | Yes | Lists tracking the completion of the packet's acceptance checks. |
| `validation` | `object` | Yes | Information regarding scenario validation and coverage. |
| `artifacts` | `object` | Yes | Pointers to generated evidence and artifacts. |
| `manifest` | `object` | Yes | Generation metadata like timestamps and schema versions. |

## Sub-Objects

### `summary`
- `result` (`string`): The main conclusion or result description.
- `key_findings` (`array` of `string`): Important outcomes or discoveries.
- `key_caveats` (`array` of `string`): Any limitations, assumptions, or caveats (optional but recommended when applicable).

### `acceptance_checks`
- `passed` (`array` of `string`): Checks that were successfully met.
- `failed` (`array` of `string`): Checks that were not met.
- `not_applicable` (`array` of `string`): Checks that did not apply to this execution.

### `validation`
- `scenario_count` (`integer`): Number of scenarios run.
- `scenario_summary` (`array` of `string`): Short descriptions of what was validated.
- `coverage_notes` (`array` of `string`): Notes on coverage gaps or specifics.

### `artifacts`
- `primary` (`array` of `string`): Keys or filenames of primary artifacts.
- `supporting` (`array` of `string`): Keys or filenames of supporting artifacts. Every supporting file must be listed here.
- `archive` (`object`): Details about the `*_PROOF_ARCHIVE.zip`, including `present` (boolean), `filename`, and `sha256`.
