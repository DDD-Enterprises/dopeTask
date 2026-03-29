# dopeTask Distribution Guide

This guide outlines the steps to distribute DopeTask (package name: `dopetask`) on PyPI using the automated GitHub Actions workflow.

## Prerequisites

1.  **PyPI Account**: Ensure you have an account on [PyPI](https://pypi.org/).
2.  **PyPI Token**:
    *   Go to your PyPI account settings > API tokens.
    *   Create a new token with "Upload" scope (or scoped to `dopetask` if it already exists).
    *   Copy the token.
3.  **GitHub Secrets**:
    *   Go to your GitHub repository settings > Secrets and variables > Actions.
    *   Create a new repository secret named `PYPI_API_TOKEN`.
    *   Paste your PyPI token as the value.

    *Note: If you have configured Trusted Publishing (OIDC) between GitHub and PyPI, you can skip the token step. The workflow is configured to attempt OIDC if the token is missing.*

## Release Process

To publish a new version of dopeTask to PyPI:

1.  **Prepare the release PR**:
    *   Update the `version` field in `pyproject.toml`.
    *   Update `src/dopetask/__init__.py`.
    *   Move the `CHANGELOG.md` notes from `Unreleased` into a versioned entry.
    *   Open a PR against `main` and merge it.

2.  **Tag the Release**:
    *   Check out the merged `main` branch.
    *   Create a git tag matching the version (must start with `v`):
        ```bash
        git tag vX.Y.Z
        ```
    *   Push the tag to GitHub:
        ```bash
        git push origin vX.Y.Z
        ```

3.  **Monitor the Workflow**:
    *   Go to the "Actions" tab in your GitHub repository.
    *   Select the "Release" workflow.
    *   Watch the job for the tag you just pushed. It will:
        *   Extract the matching release notes from `CHANGELOG.md`.
        *   Verify version consistency.
        *   Run tests and linting.
        *   Build the package (`sdist` and `wheel`).
        *   Publish to PyPI using `uv publish`.

4.  **Verify on PyPI**:
    *   Visit [https://pypi.org/project/dopetask/](https://pypi.org/project/dopetask/) to see the new release.

## Installing the New Version

Once published, users can install it via:

**Using uv (Recommended):**
```bash
uv tool install dopetask
```

**Using pip:**
```bash
pip install dopetask
```

**Using the Unified Installer:**
```bash
curl -fsSL https://raw.githubusercontent.com/DDD-Enterprises/dopeTask/main/scripts/install.sh | bash -s -- --pypi
```
