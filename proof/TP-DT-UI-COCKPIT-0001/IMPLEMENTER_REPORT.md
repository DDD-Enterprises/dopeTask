# TP-DT-UI-COCKPIT-0001 Implementer Report

## 1. Change summary

Added a read-only, rich-rendered `dopetask cockpit` command. The command collects one UiStatus payload through `collect_status()` and renders one selected view, or all seven views, then exits.

## 2. Authority used

Runtime authority: `src/dopetask/ui/status.py`, `src/dopetask/ui/report.py`, `src/dopetask/ui/runner_health.py`, `src/dopetask/ui/durability.py`, `src/dopetask/workspace.py`, and `src/dopetask/cli.py`.

Design references: the accepted documents under `out/design/TP-DT-TUI-OPUS-DESIGN-0001/`. These were used as design guidance, not runtime authority.

## 3. Files created/modified

Created:
- `src/dopetask/ui/cockpit.py`
- `src/dopetask/ui/views/__init__.py`
- `src/dopetask/ui/views/series_overview.py`
- `src/dopetask/ui/views/series_detail.py`
- `src/dopetask/ui/views/packet_detail.py`
- `src/dopetask/ui/views/runner_health.py`
- `src/dopetask/ui/views/repo_health.py`
- `src/dopetask/ui/views/asset_library.py`
- `src/dopetask/ui/views/authority_diff.py`
- `src/dopetask/ui/widgets/__init__.py`
- `src/dopetask/ui/widgets/banners.py`
- `tests/ui/cockpit/test_cockpit_views.py`
- `tests/ui/cockpit/test_banners.py`
- `task-packets/TP-DT-UI-COCKPIT-0001.json`
- `proof/TP-DT-UI-COCKPIT-0001/PROOF.json`
- `proof/TP-DT-UI-COCKPIT-0001/IMPLEMENTER_REPORT.md`

Modified:
- `src/dopetask/cli.py`

## 4. Cockpit behavior

`dopetask cockpit` defaults to `series-overview`. `--view all` renders the seven views in deterministic order. The implementation is rich-only and exits after rendering; it has no event loop or keyboard navigation.

## 5. View behavior

Implemented views: Series Overview, Series Detail, Packet Detail, Runner Health, Repo Health, Asset Library, Authority Diff, and All. Missing data renders as `unknown`, `missing`, `not configured`, or a visible selection/warning panel. Historical `EXEC_ERROR` state remains visible when UiStatus marks it historical.

## 6. Banner/authority-plane behavior

Authority banners live in `src/dopetask/ui/widgets/banners.py`. Tests assert the required Runtime, Asset, Reference, and Planning banner strings. Asset Library and Authority Diff render with non-runtime banners and expose no execution/apply affordance.

## 7. CLI behavior

Registered `dopetask cockpit` with `--view`, `--series-id`, `--tp-id`, `--refresh-runners`, `--das-path`, and `--no-color`. The command calls `run_cockpit()`, which calls `collect_status()` once and passes the payload into view renderers.

## 8. Read-only behavior

Default cockpit mode writes no files. View modules do not call `collect_status()` and do not read runtime artifacts directly. `--refresh-runners` preserves the accepted existing behavior that may refresh runner health through the UiStatus collector path.

## 9. Validation commands and results

- `python3 -m json.tool task-packets/TP-DT-UI-COCKPIT-0001.json`: exit 0
- `python3 -m json.tool proof/TP-DT-UI-COCKPIT-0001/PROOF.json`: exit 0
- `python3 -m pytest tests/ui/cockpit/ -v`: exit 0, 20 passed
- `python3 -m pytest tests/ui/test_report.py tests/ui/test_status.py tests/ui/test_runner_health.py tests/test_workspace.py -v`: exit 0, 75 passed
- `python3 -m compileall -q src tests`: exit 0
- `python3 -m dopetask cockpit --help`: exit 0
- `python3 -m dopetask cockpit --view series-overview >/tmp/dopetask_cockpit_series_overview.txt`: exit 0
- `test -s /tmp/dopetask_cockpit_series_overview.txt`: exit 0
- `python3 -m dopetask cockpit --view runner-health >/tmp/dopetask_cockpit_runner_health.txt`: exit 0
- `test -s /tmp/dopetask_cockpit_runner_health.txt`: exit 0
- `python3 -m dopetask cockpit --view all >/tmp/dopetask_cockpit_all.txt`: exit 0
- `test -s /tmp/dopetask_cockpit_all.txt`: exit 0
- `grep -n "Runtime / Execution Authority" /tmp/dopetask_cockpit_all.txt`: exit 0
- `grep -n "ASSET / TEMPLATE PLANE" /tmp/dopetask_cockpit_all.txt`: exit 0
- `grep -n "Reference" /tmp/dopetask_cockpit_all.txt`: exit 0
- `git diff --check`: exit 0
- `grep -R "import textual\|from textual" src/dopetask tests || true`: exit 0, no matches
- `grep -R "dopetask doctor\|route plan\|tp series exec" src/dopetask/ui tests/ui || true`: exit 0, no matches

## 10. Commit readiness

Commit-ready after proof JSON validation. Proof intentionally does not include the final commit SHA because that would be self-referential.

## 11. Safety boundary confirmation

No Textual, prompt_toolkit, urwid, blessed, dependency, pyproject, lockfile, runner implementation, adapter, routing scoring, mutating launcher, Asset Library execution, DAS listing/preview, audit pane, route/orchestrate Claude runner, doctor invocation, route-plan invocation, Task Packet execution, dope-agent-system write, or runtime artifact write was added.
