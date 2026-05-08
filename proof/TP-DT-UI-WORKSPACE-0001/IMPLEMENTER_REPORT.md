# TP-DT-UI-WORKSPACE-0001 Implementer Report

## 1. Change summary

Added `dopetask_schemas/workspace.schema.json`, a read-only workspace resolver at `src/dopetask/workspace.py`, and focused resolver tests in `tests/test_workspace.py`. The resolver locates dope-agent-system from an explicit path, an environment variable, or `.dopetask/workspace.yaml`, and returns `None` when nothing is configured.

## 2. Authority used

- Design authority: `out/design/TP-DT-TUI-OPUS-DESIGN-0001/*`
- Dependency proof: `proof/TP-DT-UI-CONTRACTS-0001/PROOF.json`, `proof/TP-DT-UI-AUTHMETA-0001/PROOF.json`, and `proof/TP-DT-UI-RUNNERHEALTH-0001/PROOF.json`
- Task-packet shape authority: `dopetask_schemas/task_packet.schema.json`
- YAML loader precedent: `src/dopetask/router/availability.py`
- Prior UI test conventions: `tests/ui/test_runner_health.py`

## 3. Files created/modified

Created:
- `src/dopetask/workspace.py`
- `dopetask_schemas/workspace.schema.json`
- `tests/test_workspace.py`
- `task-packets/TP-DT-UI-WORKSPACE-0001.json`
- `proof/TP-DT-UI-WORKSPACE-0001/PROOF.json`
- `proof/TP-DT-UI-WORKSPACE-0001/IMPLEMENTER_REPORT.md`

Modified: none.

## 4. Resolver behavior

`workspace_path_for_repo(repo_root)` returns `.dopetask/workspace.yaml` under the resolved repository root. `load_workspace_config(repo_root)` returns `{}` when the config file is absent and raises `WorkspaceConfigError` for malformed YAML, non-mapping YAML, unsupported top-level keys, non-string path fields, non-string or empty env override, or conflicting `dope_agent_system_path` and `das_path` values.

`resolve_dope_agent_system_path(...)` normalizes configured values with `Path.expanduser()` and `Path.resolve()`. Relative paths resolve against `repo_root`. The resolver does not require the target path to exist.

## 5. Precedence rules

Resolution order:
1. `explicit_path`
2. environment variable named by `das_path_env_override`, defaulting to `DOPE_AGENT_SYSTEM_PATH`
3. workspace `dope_agent_system_path`
4. workspace `das_path`
5. `None`

`dope_agent_system_path` is the preferred config field. `das_path` remains supported as an alias for earlier design wording.

## 6. Missing/invalid config behavior

Missing `.dopetask/workspace.yaml` is not an error. With no explicit path and no relevant env var, the resolver returns `None`.

Invalid config raises `WorkspaceConfigError` instead of guessing. The workspace schema is closed with `additionalProperties: false`, matching the fail-closed config boundary for this contract-sensitive resolver.

## 7. Validation commands and results

- `python3 -m json.tool dopetask_schemas/workspace.schema.json` -> exit 0
- `python3 -m json.tool task-packets/TP-DT-UI-WORKSPACE-0001.json` -> exit 0
- `python3 -m json.tool proof/TP-DT-UI-WORKSPACE-0001/PROOF.json` -> exit 0
- `python3 -m pytest tests/test_workspace.py -v` -> exit 0 (`16 passed`)
- `python3 -m compileall -q src tests` -> exit 0
- `git diff --check` -> exit 0
- `git status --short` -> exit 0 with only allowlisted visible files before proof force-add
- `grep -R "import textual\|from textual" src/dopetask tests || true` -> exit 0 with no output
- `grep -R "dopetask doctor\|route plan\|tp series exec" src/dopetask/workspace.py tests/test_workspace.py || true` -> exit 0 with no output
- `grep -R "/Users/hue\|/Users/" src/dopetask/workspace.py tests/test_workspace.py || true` -> exit 0 with no output
- Explicit JSON Schema validation of `workspace.schema.json` -> exit 0 (`workspace-schema-valid`)
- Explicit TaskPacket schema validation of `TP-DT-UI-WORKSPACE-0001.json` -> exit 0 (`task-packet-schema-valid`)

## 8. Commit readiness

Commit-ready if the final validation rerun remains green and `git status --short` contains only the allowlisted files. Commit message: `feat(workspace): add explicit DAS path resolver`.

This report is generated before commit. A Git commit cannot contain its own final SHA in a tracked proof file without changing that SHA. The final commit hash must be verified after commit and reported in the final response.

## 9. Safety boundary confirmation

No CLI command, `dopetask ui status`, `dopetask report`, `dopetask cockpit`, Asset Library, DAS preview/listing UI, runner health change, runner implementation change, adapter behavior change, routing scoring change, dependency change, `pyproject.toml` change, `uv.lock` change, textual import, subprocess call, network call, doctor invocation, route-plan invocation, Task Packet execution, real repository `.dopetask/workspace.yaml`, hardcoded local path fallback, or dope-agent-system write was added.
