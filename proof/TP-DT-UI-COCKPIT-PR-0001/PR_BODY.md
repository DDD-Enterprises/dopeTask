# dopeTask Cockpit: read-only rich terminal views

## Accepted Cockpit Commit

Accepted cockpit commit: `929aacfc8a01ade7e4bfcbdba8e115fce95dd99b`

## Base Dependency

The branch contains the accepted UI foundation merge commit `44e6cf6f121040a6946978de634dce3c29dfdcf2`, the accepted report/status fence commit `9c93356ce662ed0c76bcd744545d3e5b827460ee`, and the accepted cockpit commit `929aacfc8a01ade7e4bfcbdba8e115fce95dd99b`.

Remote `origin/main` was observed at `44e6cf6f121040a6946978de634dce3c29dfdcf2` when this checkpoint was prepared, so this PR currently carries the accepted fence commit in addition to the cockpit slice unless `main` advances before merge.

## Scope Summary

- read-only `dopetask cockpit`
- seven rich-rendered views
- single `collect_status()` payload
- runtime/asset/reference banners
- no event loop
- no Textual
- no mutating launchers

## Explicit Non-goals

- no Asset Library listing/preview
- no DAS execution/install/apply
- no audit panes
- no mutating launchers
- no route/orchestrate Claude runner
- no dependency changes

## Validation Summary

- cockpit tests: `python3 -m pytest tests/ui/cockpit/ -v`
- foundation regression tests: `python3 -m pytest tests/ui/test_report.py tests/ui/test_status.py tests/ui/test_runner_health.py tests/test_workspace.py -v`
- compileall: `python3 -m compileall -q src tests`
- cockpit smoke views: `series-overview`, `runner-health`, `all`
- banner grep checks: Runtime, Asset, Reference
- forbidden greps: no Textual, doctor, route plan, or task execution strings in scoped UI/tests

## Audit Verdict

ACCEPT

## Accepted Non-blocking Findings

- F-01 LOW: `planning_banner()` is defined and tested but not rendered until a future planning view exists.
- F-02 INFO: `--refresh-runners` may write `RUNNER_HEALTH.json`, but only by explicit opt-in. Default cockpit remains read-only.

## Reviewer Checklist

- Verify `dopetask cockpit --view all`.
- Verify no Textual/dependency changes.
- Verify no mutating launchers.
- Verify asset-library view is placeholder/read-only.
- Verify runner-health view preserves `unknown` and `RUNNER_NOT_IMPLEMENTED`.

## Suggested Next Phase After PR Merge

Decide between an Asset Library listing TP, Authority Diff/Audit TP, or gated launcher design. Do not start mutating launchers without a fresh audit/design gate.
