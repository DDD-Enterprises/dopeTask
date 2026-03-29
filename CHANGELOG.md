# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

### Added

- N/A

### Changed

- N/A

### Fixed

- N/A

## [0.5.7] - 2026-03-29

### Added

- Added a canonical `docs/26_SUPERVISOR_PROMPTS.md` guide covering prompt generation, prompt installation, recommended current web models, and current CLI package versions.
- Added beginner-friendly onboarding content in `docs/beginner/00A_HOW_DOPETASK_WORKS.md` and linked it into the beginner docs path.

### Changed

- Updated setup, beginner, workflow, overview, and README/PyPI docs to make `dopetask ops init`, `ops export`, `ops apply`, and `ops doctor` the primary supervisor-prompt workflow.
- Updated the default ChatGPT operator model from `gpt-5.2-thinking` to `gpt-5.4` in the operator profile and prompt-init defaults.
- Added platform overlays for ChatGPT, Claude web, Claude Code, Codex, Gemini CLI, and Copilot CLI so generated prompts are less generic for current tools.

## [0.5.6] - 2026-03-28

### Changed

- Rewrote the package `README.md` so the PyPI long description reflects the current JSON TP series workflow, canonical docs map, and installation paths without stale relative links or duplicated sections.
- Expanded package metadata in `pyproject.toml` with clearer description text, richer keywords and classifiers, and direct links for releases, documentation, and changelog.
- Included `README.md` explicitly in the sdist surface so the published package and rendered long description use the checked-in canonical README.

## [0.5.5] - 2026-03-28

### Added

- Added `dopetask tp series import` to read a strict JSON Task Packet from the clipboard, validate it structurally, and write a deterministic `<tp-id>.json` packet file for later execution.

### Changed

- Standardized repo-local dopeTask installs around `.venv-dopetask` while preserving compatibility with `.venv` and legacy `.dopetask_venv`.
- Updated package metadata and install docs to point at the current `DDD-Enterprises/dopeTask` repository.
- Consolidated the user-facing docs map around the top-level `docs/` canon, added upgrade and consumer-install guides, and reduced root-level duplicate docs to compatibility stubs plus archived artifacts.

### Fixed

- Eliminated install/runtime drift where the installer default venv name did not match the repo-local shell launcher.

## [0.5.4] - 2026-03-28

### Added

- Added canonical proof contract assets under `proof/standards`, including bundle and archive-manifest schemas plus machine-valid examples.

### Changed

- Aligned proof docs with the current `ProofAggregator` output and documented the standard proof bundle as a strict, machine-readable shape.

### Fixed

- Restored the missing proof standard files referenced by the docs and added regression tests that validate checked-in proof bundles and archive manifests against them.
- Fixed existing `ruff` violations in `tp_series` worktree cleanup and status parsing so release and CI workflows can run cleanly.

## [0.5.3] - 2026-03-27

### Added

- Consolidated `docs/01_SETUP.md` as the primary entry point for new users.

### Changed

- Updated `GEMINI.md`, `CLAUDE.md`, and `CODEX.md` to mandate the `tp series` workflow.
- Refactored `StepRunner` imports to top-level for idiomatic Python.
- Git status parsing now uses NUL-terminated output (`-z`) for robustness.

### Fixed

- Implemented real `subprocess.run` execution in `StepRunner` kernel (replaces mock).
- Added deterministic worktree cleanup in `tp series exec` via context manager.

## [0.5.2] - 2026-03-26

### Added

- Added hardened regression tests for `ProofAggregator` with zip manifest verification.
- Deterministic build hash verification and wheel smoke validation in CI.
- Tag-gated release and container distribution workflows.

### Changed

- Release flow is CI-driven from version tags with uv-native build/publish steps.

### Fixed

- Removed legacy manual release workflow to enforce a single release path.
