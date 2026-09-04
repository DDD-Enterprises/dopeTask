# Independent L3 audit — dopeTask DT-G1 governed-execution repair

You are the sole independent auditor. Your job is to FALSIFY the claims below, not to confirm them.
A confirming audit that did not seriously attempt falsification is worthless here.

## Subject (bind to these exact bytes)

Repository worktree (mounted, you have real tool access):
    /Users/hue/code/dopeTask/.worktrees/dt-g1-finality-002-a1

    FROZEN_SUCCESSOR_HEAD = 93a2fe07d8bc4eed5767ac569f7cb53a8d078715
    CANONICAL_START_HEAD  = 1bf18deae224521d82a52290da893b6a9f76cc97

RISK LANE: L3_AUTHORITY_SECURITY_BOUNDARY. This code decides whether an execution grant
authorizes running a code-writing runner against a repository. Treat every gap as material.

## Custody step (do this FIRST, with real commands)

1. `git -C <worktree> status --porcelain` — must be empty. If not, STOP and report contamination.
2. FROZEN_SUCCESSOR_HEAD is the frozen SEMANTIC head. Current HEAD may sit one proof-only commit
   ahead of it (this prompt and its staging manifest had to be committed to keep the tree clean).
   Verify that yourself and do not take it on trust:
       git -C <worktree> diff --stat 93a2fe07d8bc4eed5767ac569f7cb53a8d078715..HEAD
   Every path in that delta MUST be under `proof/`. If ANY src/, tests/, task-packets/ or
   schema path appears, a semantic change happened after freeze — STOP and report it as BLOCKING.
3. Recompute sha256 for every file in `proof/TP-DT-G1-POST-SYNC-REPAIR-FINALITY-002-A1/AUDIT_STAGING_SHA256SUMS.txt`
   and compare byte-for-byte. Report each as MATCH/MISMATCH. Do not take the listed digests on trust.
4. Do NOT modify any file. This head is frozen; any write by you invalidates the audit.

## What changed

`git -C <worktree> diff 1bf18deae224521d82a52290da893b6a9f76cc97..HEAD` is the full delta.
Four repairs are claimed (R1-R4). Each claim below is a target for falsification.

### CLAIM R2 — every governed entrypoint refuses packet read/parse failures through
`GovernedAdmissionError` with a stable machine-readable reason, and no raw `OSError` escapes.
The previous attempt at this fix was rejected by an independent audit because it guarded a
helper (`_read_raw_bytes`) that was UNREACHABLE: `TPParser.parse_file` ran first in both
`execute_task_packet` and the CLI. Your primary job is to determine whether the same class of
shadowing survives anywhere.
FALSIFY BY: driving the real public entrypoints — `dopetask.ops.tp_exec.engine.execute_task_packet`
and the `dopetask tp exec` CLI via `typer.testing.CliRunner` — NOT by calling guard helpers.
Try: missing packet, unreadable packet (chmod 000), directory-instead-of-file, malformed JSON,
schema-invalid JSON, empty file, packet that disappears between admission and use, symlink loops.
Find ANY governed input path that still raises a raw OSError/ValueError/JSONDecodeError.

### CLAIM R3 — one governed entrypoint performs exactly ONE admission orchestration, ONE
repository identity load, ONE canonical validation and ONE repository binding decision;
the legacy path performs ZERO governed resolver calls.
FALSIFY BY: instrumenting call counts yourself (monkeypatch in the namespace where each symbol is
CALLED, e.g. `dopetask.ops.tp_exec.engine.load_repo_identity`,
`dopetask.guard.governed_execution.extract_origin_url`). Check real execution, CLI dry-run, CLI
real, tmux propagation, and the legacy path. Note: `canonical_repository_identity` legitimately
runs twice per admission (grant + origin are two different inputs) — that is not duplication;
say so if you see it rather than reporting it as a finding.

### CLAIM R4 — repository identity is canonical `owner/repository` exact equality; substring and
basename-only matching are impossible in admission.
FALSIFY BY: constructing a `grant.repository` value that is admitted but should not be. Note
`grant.repository` is schema-typed only as `nonempty` — no pattern — so you have a wide space.
Try at minimum: bare substrings of the origin URL; case variants; unicode/homoglyph owners;
trailing dots/slashes; `..` path traversal; `user:pass@` credential forms; a host-in-path spoof
such as `https://evil.com/github.com/OWNER/REPO`; `%2F`-encoded separators; extremely long inputs;
IDN/punycode hosts; a repo whose name is a prefix/suffix of the real one.

### CLAIM R1 — a governed run refuses when `authority_effect.grants` omits `RUNNER_INVOCATION`
(reason `AUTHORITY_UNDERGRANT_RUNNER_INVOCATION`), refusing BEFORE any adapter/TaskExecutor
construction, and this check is exactly one positive capability check — it does NOT re-implement
generic `authority_effect` enforcement.
FALSIFY BY: (a) find a governed path that still reaches a runner without `RUNNER_INVOCATION`;
(b) check the refusal really precedes runner construction, not merely precedes runner *execution*;
(c) check the implementation has NOT over-reached into over-ceiling checks, `does_not_grant`
re-assertion, or a general authority_effect validator — over-reach is a finding here, because the
operator explicitly bounded this scope.
IMPORTANT: state clearly which layer refuses which input. Some authority probes are closed by
JSON Schema (`does_not_grant` is a `const`; `grants` is a closed enum narrowed to two members for
SINGLE_TASK_PACKET subjects) and would be refused with the admission gate deleted. Those are
SCHEMA refusals, not gate refusals. Do not credit the gate with them.

### CLAIM — preserved boundaries
`build_route_plan` is never called on the governed path; legacy planner behaviour is unchanged;
`DCPRouteAuthorization` stays schema-validated, digest-bound and POLICY_ONLY and never selects
runner/provider/model/fallback/execution authority. Try to make DCP content influence any
execution decision.

## Vacuity discipline (this matters)

For every probe you run, state whether it is genuinely non-vacuous end-to-end — i.e. whether it
would still pass if the specific gate under test were deleted. A probe that JSON Schema rejects
before admission proves nothing about the gate. Mark each probe NON_VACUOUS or SCHEMA_SHADOWED.
There is a probe script at `proof/TP-DT-G1-POST-SYNC-REPAIR-FINALITY-002-A1/REPAIR_PROBE.py`
written by the implementer. It is part of the subject under audit — treat it as a claim to be
checked, not as evidence. Write your own probes.

## Environment

Run tests/probes with `uv run --extra dev pytest` or `uv run --extra dev python` from the worktree.
A bare `python`/`.venv` resolves `dopetask` to a DIFFERENT checkout and will silently audit the
wrong tree — verify `dopetask.__file__` points inside the worktree before trusting any result.
Baseline at the canonical start head is 482 passed / 7 skipped; at the frozen head 534/7/0 is claimed.

## Required output (JSON, last thing you emit)

```json
{
  "AUDIT_SUBJECT_HEAD": "93a2fe07d8bc4eed5767ac569f7cb53a8d078715",
  "HEAD_CONFIRMED": "YES|NO",
  "WORKTREE_CLEAN": "YES|NO",
  "CUSTODY_HASH_RECOMPUTATION": "PASS|FAIL|NOT_RUN",
  "AUDITOR_MODEL_SELF_REPORTED": "<exact model id>",
  "R1_UNDERGRANT_RUNNER_INVOCATION": "PASS|FAIL",
  "R1_SCOPE_OVERREACH": "NONE|FOUND",
  "R2_ENGINE_ENTRYPOINT": "PASS|FAIL",
  "R2_CLI_DRY_RUN_ENTRYPOINT": "PASS|FAIL",
  "R2_CLI_REAL_ENTRYPOINT": "PASS|FAIL",
  "RAW_OSERROR_ESCAPES": 0,
  "R3_REAL_RESOLUTION_COUNT": 1,
  "R3_DRY_RUN_RESOLUTION_COUNT": 1,
  "R3_LEGACY_RESOLUTION_COUNT": 0,
  "R4_REPOSITORY_IDENTITY": "PASS|FAIL",
  "PLANNER_ISOLATION": "PASS|FAIL",
  "DCP_POLICY_ONLY": "PASS|FAIL",
  "LEGACY_COMPATIBILITY": "PASS|FAIL",
  "FULL_SUITE_OBSERVED": "<counts you ran yourself>",
  "PROBES_RUN": [{"probe": "...", "result": "...", "vacuity": "NON_VACUOUS|SCHEMA_SHADOWED"}],
  "FINDINGS": [{"id": "F-001", "severity": "BLOCKING|NON_BLOCKING", "claim_targeted": "R1|R2|R3|R4|BOUNDARY", "evidence": "...", "reproduction": "..."}],
  "BLOCKING_FINDINGS": 0,
  "AUDIT_VERDICT": "PASS|PASS_WITH_RISKS|FAIL|NEEDS_SUPERVISOR"
}
```

Report FAIL if any blocking finding exists. Do not repair anything. Do not write any file.
