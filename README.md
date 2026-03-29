# dopeTask

`dopeTask` is a deterministic task-packet execution kernel for high-trust engineering workflows.

It validates a Task Packet, executes one allowed path or refuses with evidence, and writes canonical artifacts that operators can inspect later. The default workflow uses JSON Task Packets and the `tp series` commands so each packet runs in its own worktree, creates one bounded commit, and accumulates into a single PR for the series.

## Guarantees

- Artifact-first: if it did not write an artifact, it did not happen.
- Refusal-first: invalid or unsafe inputs fail closed with evidence.
- Deterministic outputs: identical packet, declared inputs, and dopeTask version yield stable artifacts.
- Single-path execution: no hidden retries, no silent fallback runners, no background mutation.

## Default workflow

1. Author JSON Task Packets that conform to the task packet schema.
2. Execute each ready packet with `dopetask tp series exec <packet.json> --agent gemini`.
3. Inspect progress with `dopetask tp series status <series-id>`.
4. Finalize the completed series into one PR with `dopetask tp series finalize <series-id> --title "..."`.

Each JSON TP runs in its own git worktree, stages only allowlisted changes, creates one commit, and records authoritative runtime state in:

- `out/tp_series/<series-id>/SERIES_STATE.json`
- `out/tp_series/<series-id>/packets/<tp-id>/`
- `proof/<TP_ID>_PROOF_BUNDLE.json`

## Installation

### Install from PyPI

```bash
pip install dopetask
```

### Install with uv

```bash
uv tool install dopetask
```

### Verify

```bash
dopetask --version
dopetask doctor
```

## Consumer repository install

To wire dopeTask into another repository with repo-local pinning and launch shims:

```bash
curl -fsSL https://raw.githubusercontent.com/DDD-Enterprises/dopeTask/main/scripts/install.sh | bash
```

## Docs map

### Current user and operator docs

- [Overview](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/00_OVERVIEW.md)
- [Setup](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/01_SETUP.md)
- [Task Packet format](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/13_TASK_PACKET_FORMAT.md)
- [Workflow guide](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/22_WORKFLOW_GUIDE.md)
- [Integration guide](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/23_INTEGRATION_GUIDE.md)
- [Upgrade guide](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/24_UPGRADE_GUIDE.md)
- [Consumer install](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/25_CONSUMER_INSTALL.md)

### Beginner onboarding

- [Welcome](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/beginner/00_WELCOME.md)
- [Concepts](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/beginner/01_CONCEPTS.md)
- [Installation](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/beginner/02_INSTALLATION.md)
- [Web LLM setup](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/beginner/03_WEB_LLM_SETUP.md)
- [Beginner workflow](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/beginner/04_WORKFLOW.md)

### Legacy and maintainer docs

- [Worktrees and commit sequencing](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/20_WORKTREES_COMMIT_SEQUENCING.md)
- [TP git workflow](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/TP_GIT_WORKFLOW.md)
- [Release guide](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/90_RELEASE.md)

### Proof-contract docs

- [Proof bundle contract](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/proof/PROOF_BUNDLE_CONTRACT.md)
- [Proof archive policy](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/proof/PROOF_ARCHIVE_POLICY.md)
- [Bundle review guide](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/proof/BUNDLE_REVIEW_GUIDE.md)
- [Proof bundle schema](https://github.com/DDD-Enterprises/dopeTask/blob/main/docs/proof/DOPETASK_BUNDLE_SCHEMA.md)

## Legacy/manual paths

Legacy markdown packet and `tp git` flows remain available for manual maintainer work, but they are not the default path for new supervisor-driven execution.

## Project links

- [Repository](https://github.com/DDD-Enterprises/dopeTask)
- [Releases](https://github.com/DDD-Enterprises/dopeTask/releases)
- [Issues](https://github.com/DDD-Enterprises/dopeTask/issues)
- [Security policy](https://github.com/DDD-Enterprises/dopeTask/blob/main/SECURITY.md)
- [Contributing](https://github.com/DDD-Enterprises/dopeTask/blob/main/CONTRIBUTING.md)
