# Upgrade Guide

This guide covers the operator-facing changes introduced by the JSON TP series workflow in `dopeTask` `0.5.x`.

## Who should read this

Use this guide if you previously:

- ran new work with `dopetask tp exec <packet.json>`
- relied on markdown packets plus `commit-sequence` as the normal path
- expected one packet to own an entire stacked commit plan
- consumed proof or integration docs written before the `tp series` flow became the default

## What changed

### New default operator execution path

New supervisor-driven work is now JSON-only and runs through the series workflow:

```bash
dopetask tp series exec path/to/packet.json --agent gemini
dopetask tp series exec path/to/packet.json --agent codex --model gpt-5.3-codex
dopetask tp series status <series-id>
dopetask tp series finalize <series-id> --title "..." --body "..."
```

`dopetask tp exec` still exists as a low-level executor, but it is no longer the primary path for new multi-packet work.
When you pass `--model`, the runtime uses explicit override first, route-derived model second, and the agent default last.

### Commit behavior changed

The default JSON series flow is:

- one JSON TP
- one isolated worktree
- one allowlist-checked commit
- one cumulative PR branch per series

If you were expecting a per-step commit plan, that behavior now belongs to the legacy markdown packet + `commit-sequence` path in `docs/20_WORKTREES_COMMIT_SEQUENCING.md`.

### Series state is the authoritative runtime ledger

The authoritative state for a series now lives in:

- `out/tp_series/<series-id>/SERIES_STATE.json`
- `out/tp_series/<series-id>/SERIES_PR.json` after finalize
- `out/tp_series/<series-id>/packets/<tp-id>/` for per-packet execution artifacts

Use `dopetask tp series status <series-id>` or read `SERIES_STATE.json` directly if you need machine-readable progress.

### Proof review stays bundle-first

The canonical operator proof surface remains:

- `proof/<TP_ID>_PROOF_BUNDLE.json`

Open the proof archive only when the bundle tells you drill-down is needed.

## Packet changes you may need

Older packets or prompts that only covered steps are underspecified for the default flow. New packets should include:

- `depends_on`
- `series.id`
- `series.base_branch`
- `series.parent_tp_id`
- `series.final_packet`
- `commit.message`
- `commit.allowlist`
- `commit.verify`

See `docs/13_TASK_PACKET_FORMAT.md` for the current packet contract.

## Supervisor and implementer changes

Supervisors should now:

1. author JSON packets
2. run `dopetask tp series exec` for each ready packet
3. inspect proof and series state
4. run `dopetask tp series finalize` only after the final packet completes

Implementers should no longer assume direct coding or direct git actions are the default control plane. The kernel owns worktree creation, allowlist enforcement, and final PR opening for the series flow.

## Dopemux integration changes

If you consume dopeTask from Dopemux or another orchestrator:

- read canonical proof from `proof/<TP_ID>_PROOF_BUNDLE.json`
- read series progress from `out/tp_series/<series-id>/SERIES_STATE.json`
- treat the Dopemux adapter envelope as a derived integration object, not a dopeTask-emitted canonical artifact

See `docs/integrations/dopetask/ADAPTER_SCHEMA.md` for the normalized integration envelope.

## What did not change

- Proof bundles remain the primary execution evidence.
- Legacy markdown packet workflows remain available for maintainer-only/manual paths.
- `dopetask_schemas` versioning remains separate from the main `dopeTask` app version.

## Recommended upgrade steps

1. Upgrade the installed CLI to the current `dopeTask` release.
2. Regenerate supervisor prompts with `dopetask ops export` or reapply them with `dopetask ops apply`.
3. Update supervisor prompts and local runbooks to use `tp series exec`, `status`, and `finalize`.
4. Update any packet generators so they emit `depends_on`, `series`, and `commit`.
5. Update any integrations that assumed a top-level `status` field in `SERIES_STATE.json`; the stable status summary now lives under `counts`, with packet details under `packets`.
6. Keep legacy `commit-sequence` usage only where you intentionally need the old maintainer path.

## Documentation note

A broader doc audit is helpful but not required for day-to-day use of `0.5.x`.

The most useful follow-up audit would focus on:

- stale integration examples
- redundant install/setup references
- older commit-plan language that predates the JSON TP series workflow

## Focused cleanup backlog

The current docs cleanup intentionally leaves these areas as separate follow-up work rather than folding them into the main user path:

- audit artifact maintenance under `docs/91_*` through `docs/94_*`
- deep proof-document cross-link cleanup beyond the canonical proof pages
- any future pruning of legacy/manual maintainer docs after downstream links are confirmed
