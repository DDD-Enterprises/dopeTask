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
