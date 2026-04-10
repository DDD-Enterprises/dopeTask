# Runtime-Help Reconciliation Scan

## Surfaces reviewed
- docs/22_WORKFLOW_GUIDE.md
- docs/23_INTEGRATION_GUIDE.md
- docs/13_TASK_PACKET_FORMAT.md
- `python -m dopetask --help`
- `python -m dopetask tp series --help`
- `python -m dopetask tp exec --help`
- `python -m dopetask route --help`

## 1. Doc claims that match runtime help
- The docs consistently present `tp series` as the default operator path, and runtime help exposes `tp series` as a first-class command group with `exec`, `status`, and `finalize`.
- `docs/22_WORKFLOW_GUIDE.md` matches runtime help on the core `tp series` lifecycle surfaces: `exec`, `status`, and `finalize`.
- `docs/23_INTEGRATION_GUIDE.md` correctly treats `tp exec` and `route` as separate non-default surfaces; runtime help exposes both `tp exec` and `route` independently.
- `docs/13_TASK_PACKET_FORMAT.md` correctly frames JSON Task Packets as the default supervisor path for current work; runtime help exposes `tp series` as the relevant command family.

## 2. Doc claims that still exceed or mismatch runtime help
- `docs/13_TASK_PACKET_FORMAT.md` still says operators can "import clipboard JSON with `dopetask tp series import`", but `python -m dopetask tp series --help` currently lists only `exec`, `status`, and `finalize`.
- `docs/23_INTEGRATION_GUIDE.md` says the low-level JSON TP executor currently implements only the `gemini` agent profile in the runtime path, but `python -m dopetask tp exec --help` advertises `gemini`, `codex`, and `vibe`.

## 3. Remaining operator-facing drift risks
- Top-level runtime help still exposes many legacy and alternate surfaces (`orchestrate`, `commit-sequence`, `loop`, `run-task`, `finish`) that the repaired docs intentionally de-emphasize. That is a framing improvement, but it still leaves room for operators to infer multiple competing "main" paths from CLI help alone.
- The `tp series import` mismatch is a direct operator-facing trust risk because it names a concrete command that is not visible in the exposed `tp series` help surface used for discovery.
- The agent-profile mismatch in `tp exec` is another trust risk because users reading the integration guide could assume only `gemini` is valid when runtime help advertises a broader supported set.

## 4. Recommended next cleanup target
- First: `docs/13_TASK_PACKET_FORMAT.md`, to reconcile the `tp series import` claim with the currently exposed `tp series` help surface.
- Second: `docs/23_INTEGRATION_GUIDE.md`, to reconcile the "only gemini" claim with the currently exposed `tp exec` help output.
- After that: decide whether top-level help needs a separate orientation doc or whether the current doc set is intentionally sufficient despite the broader CLI surface.
