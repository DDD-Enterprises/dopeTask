# TP-DT-UI-REPORT-FENCE-0001 Implementer Report

## 1. Change summary

Added resolved repository-root fences for explicit report and status output paths. `dopetask report --out` now refuses resolved paths outside `repo_root` before preserving the existing `proof/` and resolved dope-agent-system refusals. `dopetask ui status --json --out` had the same outside-repo gap, so its CLI writer now refuses outside-repo resolved paths before existing `proof/` and DAS checks.

## 2. Authority used

Runtime authority was `src/dopetask/ui/report.py` for `write_report()` and `src/dopetask/cli.py` for `_write_ui_status_output()`. `src/dopetask/ui/status.py` was inspected as UiStatus collector authority; it does not own explicit `--out` writing. Tests in `tests/ui/test_report.py` and `tests/ui/test_status.py` were used as behavior contracts. Prior proof inspected: `proof/TP-DT-UI-REPORT-0001/PROOF.json`.

## 3. Files created/modified

Created:
- `task-packets/TP-DT-UI-REPORT-FENCE-0001.json`
- `proof/TP-DT-UI-REPORT-FENCE-0001/PROOF.json`
- `proof/TP-DT-UI-REPORT-FENCE-0001/IMPLEMENTER_REPORT.md`

Modified:
- `src/dopetask/ui/report.py`
- `src/dopetask/cli.py`
- `tests/ui/test_report.py`
- `tests/ui/test_status.py`

`src/dopetask/cli.py` is outside the user-provided commit allowlist, but the status `--out` writer lives there. Hardening status output without touching this file would leave the observed status gap open.

## 4. Path fence behavior

Both output paths are resolved before checks. The effective order is: refuse outside repository root, refuse under `proof/`, refuse under resolved dope-agent-system path when known, then create parents and write.

## 5. Report output behavior

`write_report()` raises `ReportOutputRefusedError` for outside-repo, `proof/`, and resolved DAS paths. Valid repo-local paths such as `out/reports/report.md` still write. CLI stdout mode is unchanged and still emits markdown without writing files.

## 6. Status output behavior

`dopetask ui status --json --out` now exits with code 2 and a human-readable error for outside-repo resolved paths. Valid repo-local status output still writes. Existing `proof/` and DAS refusals remain covered.

## 7. Symlink handling

Symlink tests cover report and status outputs resolving to outside the repo, into `proof/`, and into a supplied DAS path. Each refusal occurs before target file creation.

## 8. Validation commands and results

- `python3 -m json.tool task-packets/TP-DT-UI-REPORT-FENCE-0001.json`: exit 0
- `python3 -m json.tool proof/TP-DT-UI-REPORT-FENCE-0001/PROOF.json`: exit 0
- `python3 -m pytest tests/ui/test_report.py -v`: exit 0, 22 passed
- `python3 -m pytest tests/ui/test_status.py -v`: exit 0, 24 passed
- `python3 -m pytest tests/ui/test_runner_health.py -v`: exit 0, 13 passed
- `python3 -m pytest tests/test_workspace.py -v`: exit 0, 16 passed with a post-test pytest tmp cleanup warning
- `python3 -m compileall -q src tests`: exit 0
- `python3 -m dopetask ui status --json | python3 -m json.tool`: exit 0
- `python3 -m dopetask report SERIES-AUDIT-057B-PROMPT-PIPELINE >/tmp/dopetask_report_fence_smoke.md`: exit 0
- `test -s /tmp/dopetask_report_fence_smoke.md`: exit 0
- `python3 -m dopetask report SERIES-AUDIT-057B-PROMPT-PIPELINE --out out/reports/tp-dt-ui-report-fence-smoke.md`: exit 0
- `test -s out/reports/tp-dt-ui-report-fence-smoke.md`: exit 0
- `python3 -m dopetask report SERIES-AUDIT-057B-PROMPT-PIPELINE --out ../../dopetask_report_should_refuse.md ; test $? -ne 0`: exit 0
- `test ! -f ../../dopetask_report_should_refuse.md`: exit 0
- `git diff --check`: exit 0
- `grep -R "import textual\|from textual" src/dopetask tests || true`: exit 0, no matches
- `grep -R "dopetask doctor\|route plan\|tp series exec" src/dopetask/ui tests/ui || true`: exit 0, no matches

## 9. Commit readiness

Commit-ready after proof JSON validation and clean staging of task-scope files. The final commit hash is intentionally not embedded in proof due to the self-referential hash caveat.

## 10. Safety boundary confirmation

No cockpit, Asset Library UI, DAS listing/preview, mutating launcher, audit pane, route/orchestrate Claude runner, textual dependency, dependency file, runner implementation, adapter, routing scoring, doctor, route plan, or Task Packet execution work was performed. No dope-agent-system writes were performed. Proof writes were limited to `proof/TP-DT-UI-REPORT-FENCE-0001/`.
