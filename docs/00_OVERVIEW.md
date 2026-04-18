# Overview

dopeTask is a deterministic execution kernel for task packets.

## What it is

dopeTask enforces a narrow contract:

- determinism for planning and execution artifacts
- refusal when policy, scope, or evidence constraints are violated
- artifacts as the source of truth for what happened
- one path in auto mode, or an explicit handoff in manual mode

## What it is not

dopeTask is not a generic orchestration platform. It does not provide hidden retries, implicit fallbacks, or background side effects.

## Kernel boundary

The kernel validates inputs, selects one deterministic route, executes that route, and exits after writing canonical artifacts.

Scheduling, memory, UX layers, and long-running orchestration belong to external systems.

## Operating promise

Given the same packet, declared inputs, and dopeTask version, output artifacts and refusal behavior are stable.

## Docs map

### Current user/operator docs

- `01_SETUP.md`
- `13_TASK_PACKET_FORMAT.md`
- `22_WORKFLOW_GUIDE.md`
- `23_INTEGRATION_GUIDE.md`
- `24_UPGRADE_GUIDE.md`
- `25_CONSUMER_INSTALL.md`
- `26_SUPERVISOR_PROMPTS.md`

### Supporting reference docs

- `10_ARCHITECTURE.md`
- `11_PUBLIC_CONTRACT.md`
- `12_ROUTER.md`
- `14_PROJECT_DOCTOR.md`

### Beginner onboarding

- `beginner/00_WELCOME.md`
- `beginner/00A_HOW_DOPETASK_WORKS.md`
- `beginner/01_CONCEPTS.md`
- `beginner/02_INSTALLATION.md`
- `beginner/03_WEB_LLM_SETUP.md`
- `beginner/04_WORKFLOW.md`

### Legacy/manual maintainer docs

- `20_WORKTREES_COMMIT_SEQUENCING.md`
- `TP_GIT_WORKFLOW.md`

### Proof-contract docs

- `proof/PROOF_BUNDLE_CONTRACT.md`
- `proof/PROOF_ARCHIVE_POLICY.md`
- `proof/BUNDLE_REVIEW_GUIDE.md`
- `proof/DOPETASK_BUNDLE_SCHEMA.md`

### Audit artifact docs

- `91_CONTRACT_AUDIT_SCHEMA.md`
- `92_CONTRACT_CLAIMS_INVENTORY.md`
- `93_CONTRACT_AUDIT_REPORT.md`
- `94_CONTRACT_REMEDIATION_BACKLOG.md`
- `archive/ROOT_ARTIFACTS.md`

## Focused audit notes

This overview intentionally excludes the audit artifact set from the main user navigation path.

Known cleanup goals addressed by the current docs structure:

- JSON TP series docs are the default execution path.
- Low-level `tp exec` remains a separate execution plane and currently supports `gemini` and `codex`.
- Route/orchestrate remains a separate execution plane and now includes a real `codex_desktop` runner path, but it is still not the default operator workflow.
- Beginner docs are onboarding/tutorial material, not the canonical contract.
- Legacy markdown packet and `tp git` docs remain available but are clearly non-default.
- Integration and upgrade docs are first-class entrypoints for current users.
