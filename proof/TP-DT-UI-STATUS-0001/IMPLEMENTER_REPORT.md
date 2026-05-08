# TP-DT-UI-STATUS-0001 Implementer Report

## 1. Change summary

Added a read-only UI status data layer for later report and cockpit surfaces. The change includes `dopetask_schemas/ui_status.schema.json`, `src/dopetask/ui/status.py`, `src/dopetask/ui/durability.py`, focused tests, and a minimal `dopetask ui status --json` CLI command.

## 2. Authority used

- Design authority: `out/design/TP-DT-TUI-OPUS-DESIGN-0001/*`
- Dependency proof: `proof/TP-DT-UI-CONTRACTS-0001/PROOF.json`, `proof/TP-DT-UI-AUTHMETA-0001/PROOF.json`, `proof/TP-DT-UI-RUNNERHEALTH-0001/PROOF.json`, and `proof/TP-DT-UI-WORKSPACE-0001/PROOF.json`
- Runtime artifact schemas: `dopetask_schemas/series_state.schema.json`, `exec_record.schema.json`, `exec_error.schema.json`, `series_context.schema.json`, `route_plan.schema.json`, `runner_health.schema.json`, and `workspace.schema.json`
- Existing read-only APIs: `src/dopetask/ui/runner_health.py` and `src/dopetask/workspace.py`
- CLI registration precedent: `src/dopetask/cli.py`

## 3. Files created/modified

Created:
- `src/dopetask/ui/status.py`
- `src/dopetask/ui/durability.py`
- `dopetask_schemas/ui_status.schema.json`
- `tests/ui/test_status.py`
- `task-packets/TP-DT-UI-STATUS-0001.json`
- `proof/TP-DT-UI-STATUS-0001/PROOF.json`
- `proof/TP-DT-UI-STATUS-0001/IMPLEMENTER_REPORT.md`

Modified:
- `src/dopetask/cli.py`

## 4. Collector behavior

`collect_status(repo_root, refresh_runner_health=False, das_path=None)` reads cached runtime artifacts under `out/tp_series`, cached runner health, cached doctor report, cached route plan, git metadata, and workspace/DAS resolver state. Missing `out/tp_series` returns an empty `series` array without error. The default collector does not write files.

Each series reads `SERIES_STATE.json` as current state authority. Packet summaries preserve EXEC metadata when present, including `agent`, `model`, `requested_model`, `effective_model`, `effective_model_source`, `auth_mode`, and `bare_mode_used`. Missing `auth_mode` becomes `unknown`.

`EXEC_ERROR.json` presence is represented as historical error evidence. It is marked current only when the SERIES_STATE packet status is `failed` and the error record corresponds to the packet.

## 5. Durability behavior

`classify_artifact_path(repo_root, path)` returns `tracked-in-git`, `local-only-gitignored`, `untracked-not-ignored`, or `missing`, plus path kind and existence. The implementation uses `git ls-files --error-unmatch` and `git check-ignore -v`; it does not rely on string heuristics for git state.

Rendered artifact paths carry durability metadata, including runner health, series state, packet context, exec, exec error, proof bundle, cached doctor report, and cached route plan paths.

## 6. CLI behavior

Registered only `dopetask ui status`. Supported forms:
- `dopetask ui status --json`
- `dopetask ui status --json --out <path>`
- `dopetask ui status --json --refresh-runners`
- `dopetask ui status --json --das-path <path>`

Output is JSON to stdout. `--out` writes the same JSON to the requested path and creates only that path's parents. `--out` under `proof/` is refused. `--out` under the resolved dope-agent-system path is refused when that path is known.

## 7. Missing/invalid artifact behavior

Missing cached artifacts are represented as absent or `missing` durability, not as collector failure. Invalid JSON or schema-invalid runtime artifacts produce error markers with path metadata. A bad series or packet artifact does not prevent other series or artifacts from being represented.

## 8. Validation commands and results

- `python3 -m json.tool dopetask_schemas/ui_status.schema.json` -> exit 0
- `python3 -m json.tool task-packets/TP-DT-UI-STATUS-0001.json` -> exit 0
- `python3 -m json.tool proof/TP-DT-UI-STATUS-0001/PROOF.json` -> exit 0
- `python3 -m pytest tests/ui/test_status.py -v` -> exit 0 (`20 passed`)
- `python3 -m pytest tests/ui/test_runner_health.py -v` -> exit 0 (`13 passed`)
- `python3 -m pytest tests/test_workspace.py -v` -> exit 0 (`16 passed`)
- `python3 -m pytest tests/schemas/test_runtime_artifact_schemas.py -v` -> exit 0
- `python3 -m compileall -q src tests` -> exit 0
- `python3 -m dopetask ui status --json | python3 -m json.tool` -> exit 0
- `python3 -m dopetask ui status --json --out /tmp/dopetask_ui_status_tp_dt_ui_status_0001.json` -> exit 0
- `python3 -m json.tool /tmp/dopetask_ui_status_tp_dt_ui_status_0001.json` -> exit 0
- Explicit JSON Schema validation of `/tmp/dopetask_ui_status_tp_dt_ui_status_0001.json` -> exit 0 (`ui-status-artifact-schema-valid`)
- `git diff --check` -> exit 0
- `git status --short` -> exit 0 with only allowlisted visible files before proof force-add
- `grep -R "import textual\|from textual" src/dopetask tests || true` -> exit 0 with no output
- `grep -R "dopetask doctor\|route plan\|tp series exec" src/dopetask/ui tests/ui || true` -> exit 0 with no output

## 9. Commit readiness

Commit-ready if the final validation rerun remains green and `git status --short` contains only the allowlisted files. Commit message: `feat(ui): add read-only status collector`.

This report is generated before commit. A Git commit cannot contain its own final SHA in a tracked proof file without changing that SHA. The final commit hash must be verified after commit and reported in the final response.

## 10. Safety boundary confirmation

No `dopetask report`, `dopetask cockpit`, Asset Library UI, DAS file listing or preview, mutating launcher, audit pane, dependency change, `pyproject.toml` change, `uv.lock` change, runner implementation change, adapter behavior change, routing scoring change, textual import, doctor invocation, route-plan invocation, task execution, dope-agent-system write, proof write outside this TP, or direct write to SERIES_STATE/EXEC/EXEC_ERROR/SERIES_CONTEXT/ROUTE_PLAN/proof bundle/out-tp-series artifacts was added.
