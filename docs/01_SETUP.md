# Setup and Tool Configuration

This guide covers the necessary steps to set up your environment to use `dopeTask`.

## Prerequisites

1.  **Python**: Python 3.9 or newer is required.
2.  **GitHub CLI**: The `gh` command-line tool is required for creating pull requests with `dopetask tp series finalize`.
    -   **Installation**: Follow the [official installation instructions](https://github.com/cli/cli#installation).
    -   **Authentication**: After installing, run:
        ```bash
        gh auth login
        ```

## Installation

To install `dopeTask` for development, clone the repository and install it in editable mode:

```bash
git clone https://github.com/DDD-Enterprises/dopeTask.git
cd dopeTask
pip install -e .
```

Alternatively, if you are using `uv`:

```bash
uv sync
```

## Configuration

`dopeTask` is designed to be zero-config for most projects. However, you should ensure your environment has the following set up:

-   **Environment Variables**: Ensure `GITHUB_TOKEN` is set if you are running in a CI environment where `gh auth login` is not practical.
-   **Path**: Ensure the `scripts/` directory is in your `PATH` if you want to use the repository shims.
-   **Repo-local venvs**: The repo-local launcher prefers `.venv-dopetask`, then `.venv`, then legacy `.dopetask_venv`.

## Verification

Verify your installation by running the `doctor` command:

```bash
dopetask doctor
```

And checking the version:

```bash
dopetask --version
```
