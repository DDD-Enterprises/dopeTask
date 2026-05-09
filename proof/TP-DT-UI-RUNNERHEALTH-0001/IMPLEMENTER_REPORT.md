# TP-DT-UI-RUNNERHEALTH-0001 Implementer Report

## 1. Change summary

Added `dopetask_schemas/runner_health.schema.json`, a read-only runner health probe at `src/dopetask/ui/runner_health.py`, and a minimal `dopetask ui runners` CLI surface. The CLI supports JSON output and writes `out/dopetask_ui/RUNNER_HEALTH.json` only when `--refresh` is supplied.

## 2. Authority used

- Design authority: `out/design/TP-DT-TUI-OPUS-DESIGN-0001/*`
- Dependency proof: `proof/TP-DT-UI-CONTRACTS-0001/PROOF.json` and `proof/TP-DT-UI-AUTHMETA-0001/PROOF.json`
- Availability source: `src/dopetask/router/availability.py` and `src/dopetask/router/types.py`
- Route-plane source: `src/dopetask/runners/__init__.py` plus runner adapter files under `src/dopetask/runners/`
- TP-series source: packages under `src/dopetask_adapters/`
- CLI source: `src/dopetask/cli.py`

## 3. Files created/modified

Created:
- `dopetask_schemas/runner_health.schema.json`
- `src/dopetask/ui/__init__.py`
- `src/dopetask/ui/runner_health.py`
- `tests/ui/test_runner_health.py`
- `task-packets/TP-DT-UI-RUNNERHEALTH-0001.json`
- `proof/TP-DT-UI-RUNNERHEALTH-0001/PROOF.json`
- `proof/TP-DT-UI-RUNNERHEALTH-0001/IMPLEMENTER_REPORT.md`

Modified:
- `src/dopetask/cli.py`

## 4. Runner health model

The runner health payload reports `configured`, `binary_present`, `binary_path`, `auth_ready`, `auth_probe_method`, `tp_series_adapter`, `route_plane_adapter`, `overall_health`, and `notes` for each known runner. The known runner set is the union of route-plane runners from `RUNNER_NAMES` and TP-series adapter names that exist under `src/dopetask_adapters/`.

Configured state comes from `.dopetask/runtime/availability.yaml` when present. Missing config is reported as `configured: "missing-config"`. Binary state uses `shutil.which` only. Auth readiness defaults to `unknown` with `auth_probe_method: "not_implemented"`.

Route-plane adapter state is derived from `src/dopetask/runners.RUNNER_ADAPTERS` and source inspection of `run()` methods for `RUNNER_NOT_IMPLEMENTED` stubs. TP-series adapter state is derived from `src/dopetask_adapters` module presence, mapping `codex_desktop` to the `codex` TP-series adapter.

## 5. CLI behavior

Registered only:
- `dopetask ui runners --json`
- `dopetask ui runners --refresh --json`

No `dopetask ui status`, `dopetask report`, or `dopetask cockpit` command was added. Output is machine-readable JSON. The `--json` option is accepted for the TP contract; JSON remains the only output shape.

## 6. Artifact write behavior

Default collection and `dopetask ui runners --json` do not write `RUNNER_HEALTH.json`. `collect_runner_health(..., refresh=True)` and `dopetask ui runners --refresh --json` write only `out/dopetask_ui/RUNNER_HEALTH.json`. That artifact is runtime output under ignored `out/` and was not added to git.

## 7. Validation commands and results

- `python3 -m json.tool dopetask_schemas/runner_health.schema.json` -> exit 0
- `python3 -m json.tool task-packets/TP-DT-UI-RUNNERHEALTH-0001.json` -> exit 0
- `python3 -m json.tool proof/TP-DT-UI-RUNNERHEALTH-0001/PROOF.json` -> exit 0
- `python3 -m pytest tests/ui/test_runner_health.py -v` -> exit 0 (`13 passed`)
- `python3 -m compileall -q src tests` -> exit 0
- `python3 -m dopetask ui runners --json | python3 -m json.tool` -> exit 0
- `python3 -m dopetask ui runners --refresh --json | python3 -m json.tool` -> exit 0
- `python3 -m json.tool out/dopetask_ui/RUNNER_HEALTH.json` -> exit 0
- Explicit JSON Schema validation of `out/dopetask_ui/RUNNER_HEALTH.json` -> exit 0 (`runner-health-artifact-schema-valid`)
- Sequential refresh stdout/artifact comparison -> exit 0 (`runner-health-refresh-artifact-match`)
- `git diff --check` -> exit 0
- `git status --short` -> exit 0 with only allowlisted visible source/test/task-packet changes
- `grep -R "import textual\|from textual" src/dopetask tests || true` -> exit 0 with no output
- `grep -R "dopetask doctor\|route plan\|tp series exec" src/dopetask/ui tests/ui || true` -> exit 0 with no output

## 8. Commit hash if committed

This report is generated before commit. A Git commit cannot contain its own final SHA in a tracked proof file without changing that SHA. The final commit hash must be verified after commit and reported in the final response.

## 9. Final git status

Pre-commit visible status:

```text
 M src/dopetask/cli.py
?? dopetask_schemas/runner_health.schema.json
?? src/dopetask/ui/
?? task-packets/TP-DT-UI-RUNNERHEALTH-0001.json
?? tests/ui/
```

Ignored runtime output: `out/dopetask_ui/RUNNER_HEALTH.json`.

## 10. Safety boundary confirmation

No status collector, report command, cockpit command, workspace resolver, DAS asset library, audit panes, mutating launchers, textual import, dependency change, `pyproject.toml` change, `uv.lock` change, runner implementation change, adapter behavior change, routing scoring change, doctor invocation, route-plan invocation, task execution, or dope-agent-system write was made.
