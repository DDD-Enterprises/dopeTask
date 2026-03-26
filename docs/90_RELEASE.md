# Release Process (Maintainers)

This guide details the release process for dopeTask maintainers.

PyPI package name: `dopetask`  
CLI entrypoint after install: `dopetask`

## Release Process

1. Land the release changes in a PR against `main`
2. Merge the PR
3. Tag `main` with `git tag vX.Y.Z`
4. Push the tag
5. CI builds, publishes, and creates the GitHub release from the changelog entry

## Release checklist

1. Update version in both version sources of truth
2. Move release notes from `Unreleased` into a dated version entry in `CHANGELOG.md`
3. Open and merge the release PR
4. Verify locally from merged `main`
5. Tag and publish from CI

## Preparing the release

### Bump version

Update the version string in two locations:

1. `src/dopetask/__init__.py`
2. `pyproject.toml`

Commit these changes on a release branch / PR:

```bash
git add src/dopetask/__init__.py pyproject.toml
git commit -m "chore: bump version to X.Y.Z"
```

### Verify locally

Run tests:

```bash
uv run pytest
```

Build artifacts locally for verification only:

```bash
uv build
```

Do not publish from laptops or local developer machines. Publishing occurs in CI only after a release tag is pushed.

If you want the repo’s local verification wrapper, run:

```bash
bash scripts/dopetask_release_local.sh
```

The local wrapper requires a clean working tree and is intended to run after the release PR is merged or from a clean release branch.

Do not use `scripts/release.sh` for version bumps or tagging. It is a guarded helper that now points back to the PR-first release flow in this document.

## Tagging and publishing

After the release PR is merged into `main`, create a tag matching your version (must start with `v`):

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

Pushing a tag should trigger the release workflow in CI.

## Automated workflow

After pushing the tag, your GitHub Actions release workflow should:

1. Verify tag matches `pyproject.toml` version
2. Extract the matching version entry from `CHANGELOG.md` for the GitHub Release body
3. Install dependencies with a frozen lockfile
4. Run lint (`ruff`) and typecheck (`mypy`)
5. Run tests in a clean environment
6. Build sdist and wheel
7. Smoke test install and `dopetask --help`
8. Publish artifacts from CI only

## Security & Provenance Gates

1. Release artifact provenance attestation is generated in CI.
2. Release hashes are generated in CI for the built distribution files.
3. Release remains tag-gated and fails on tag/version mismatch.

## Provenance Expectations

1. Release artifacts are built in CI on tag push (`vX.Y.Z`).
2. Release hashes are generated in CI and recorded with the release artifacts.
3. Local machines never perform direct publish operations for release artifacts.
