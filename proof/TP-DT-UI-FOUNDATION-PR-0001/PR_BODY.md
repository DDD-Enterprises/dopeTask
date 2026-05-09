# dopeTask UI Foundation: schemas, auth metadata, runner/workspace/status/report

## Accepted TP Sequence

- `TP-DT-UI-CONTRACTS-0001`: `853e75b4d5a557f786808d7c8571ae4a7b29d66a`
- `TP-DT-UI-AUTHMETA-0001`: `fe59e06eea2ec394df4addc05a1c1061f9bcaf41`
- `TP-DT-UI-RUNNERHEALTH-0001`: `2fff7d921058666358c11f931b18fdc5ab3972bc`
- `TP-DT-UI-WORKSPACE-0001`: `715be219f79b06ba01abb479a98b987f031c7b1d`
- `TP-DT-UI-STATUS-0001`: `8c50b3c36548ad70835956ef86e2cd52d6e5131d`
- `TP-DT-UI-REPORT-0001`: `f77081d774085c0e8455517a8c9a499f7fb790cb`

## Scope Summary

- Runtime artifact schemas for series state, execution records, execution errors, series context, route plans, runner health, workspace config, and UiStatus.
- Auth/runtime metadata surfaced through execution records and proof aggregation.
- Read-only runner health probe and schema.
- Workspace/DAS path resolver with explicit config and environment-variable support.
- Read-only UiStatus collector with artifact durability classification.
- Markdown `dopetask report <series_id>` command rendered from UiStatus.

## Explicit Non-Goals

- No cockpit.
- No Asset Library UI.
- No mutating launchers.
- No audit panes.
- No textual.
- No dependency changes.
- No DAS writes.
- No route/orchestrate Claude runner.

## Validation Summary

Accepted TP proof artifacts record focused JSON schema checks, pytest suites, compile checks, CLI smoke checks, git diff checks, and safety grep checks. This checkpoint adds no runtime source changes; it packages the accepted foundation slice for review.

## Accepted Risks

- The self-referential proof hash caveat is accepted.
- `dopetask report --out` refuses `proof/` and DAS paths as required, but does not enforce a general repo-root-only output fence. This is accepted as non-blocking hardening debt.
- The report renderer reads UiStatus key names directly. This is accepted as first-pass renderer maintenance debt.

## Reviewer Checklist

- Verify `dopetask report <series_id>`.
- Verify status collector read-only boundaries.
- Verify durability/auth rendering.
- Verify no dependency changes.
- Verify proof files are tracked.

## Suggested Next Phase After PR Merge

- `TP-DT-UI-COCKPIT-0001` only after PR review and merge.
- Or a narrow hardening TP for a report `--out` repo-root fence if reviewers prefer to address that before cockpit work.
