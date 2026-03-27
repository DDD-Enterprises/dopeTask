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

## [0.5.1] - 2026-03-26

### Added

- Added hardened regression tests for `ProofAggregator` with zip manifest verification.

### Changed

- Reconciled standard proof bundle contract with the runtime writer authority.
- Removed non-standard `decision` and `dopetask` blocks from the core proof bundle contract.
- Normalized historical proof bundles and aligned documentation with emitted artifact reality.
- Corrected archive manifest definition to use `filename` instead of `path`.

## [0.5.0] - 2026-03-26

### Added

- Added DAG-aware JSON TP series execution with `depends_on`, `series`, and `commit` metadata plus `dopetask tp series exec`, `status`, and `finalize`.
- Added an authoritative per-series ledger and dependency context artifacts for multi-packet supervisor workflows.

### Changed

- Made JSON TaskPackets the default documented format for new supervisor-driven work and demoted legacy markdown / `tp git` flows to manual-maintainer paths.
- Updated supervisor/operator prompts, beginner docs, release docs, and release automation to match the TP-series workflow and changelog-driven release notes.
- Bumped dopeTask to version `0.5.0`.

### Fixed

- Corrected release helper script references to the current local build and clean-venv verification scripts.

## [0.2.0] - 2026-03-03

### Added

- Added a migration guide for Dopemux users moving from the legacy product naming to dopeTask naming.
- Added Python 3.9 compatibility coverage for TOML parsing and adapter entry-point discovery.

### Changed

- Completed the repo-wide legacy-name to dopeTask rebrand across install docs, project instructions, release guidance, and packaged assets.
- Lowered the supported Python floor from 3.11 to 3.9.
- Updated packaging metadata, lint/type targets, and lock resolution to support Python 3.9+ environments.

### Fixed

- Removed Python 3.10+/3.11-only syntax and stdlib assumptions that blocked installation or runtime use on Python 3.9.

## [0.1.3] - 2026-02-21

### Added

- No user-facing features; release focused on public-release hardening.

### Changed

- Renamed the PyPI distribution to `dopetask` (previously `dopetask-kernel`).
- Unified package metadata and runtime versioning to `0.1.3`.
- Hardened tag-driven release workflow with frozen dependency sync and pre-publish lint/type/test gates.

### Fixed

- Resolved `ruff` and `mypy` gate failures in CLI/ops/guard code paths.
- Removed duplicate `wt start`, `commit-sequence`, and `finish` command definitions from CLI registration.
- Removed broken legacy/placeholder workflows that were not operable in this repository state.

## [0.1.0] - 2026-02-21

### Added

- Initial public release baseline.
- Deterministic build hash verification and wheel smoke validation in CI.
- Tag-gated release and container distribution workflows.

### Changed

- Release flow is CI-driven from version tags with uv-native build/publish steps.

### Fixed

- Removed legacy manual release workflow to enforce a single release path.
