# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

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
