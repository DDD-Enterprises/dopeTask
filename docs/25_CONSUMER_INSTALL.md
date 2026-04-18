# Consumer Install Guide

This guide covers installing `dopeTask` into another repository without vendoring the source tree.

Use this guide if you are wiring `dopeTask` into a downstream project such as Dopemux or another consumer repository.

## Quick install

Run this from the downstream repository root:

```bash
curl -fsSL https://raw.githubusercontent.com/DDD-Enterprises/dopeTask/main/scripts/install.sh | bash
```

This will:

- detect the repository root
- create `.dopetask-pin` if one does not exist
- create or reuse a repo-local virtual environment
- install `dopeTask`

## Verify the install

```bash
source .venv-dopetask/bin/activate
dopetask --version
dopetask doctor --timestamp-mode deterministic
```

If the repository already uses `.venv` or the legacy `.dopetask_venv`, the launcher will reuse those environments.

## Strict packet pack

If the downstream repository wants the strict repo-aware contract, add the policy schema pack and update its bootstrap prompts after installing dopeTask:

- `dopetask_schemas/task_packet.strict.schema.json`
- strict packet examples for repo-bound work
- repo instruction text that tells supervisors to emit `repo_binding`, `execution`, `commit.verify`, `pr`, and Gemini PAL metadata when applicable

For a fresh downstream repository, run `dopetask project shell init`, then `dopetask ops init`, then `dopetask ops apply` so the installed prompt and repo instruction files explain the strict contract.

## Pinning and upgrades

You can pin the install through `.dopetask-pin` and upgrade later with:

```bash
dopetask upgrade --latest
```

or:

```bash
dopetask upgrade --version vX.Y.Z
```

For release and distribution policy, see `DISTRIBUTION_GUIDE.md`. For workflow migration notes, see `24_UPGRADE_GUIDE.md`.
