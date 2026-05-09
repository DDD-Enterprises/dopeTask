"""Regression tests for scoped tp-series proof artifact handling."""

from __future__ import annotations

from pathlib import Path

from dopetask.ops.tp_series.logic import _cleanup_generated_files, _copy_proof_artifacts


def _write_files(root: Path, names: list[str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for name in names:
        (root / name).write_text(f"{name}\n", encoding="utf-8")


def test_copy_proof_artifacts_only_copies_current_tp_files(tmp_path: Path) -> None:
    worktree_path = tmp_path / "worktree"
    run_dir = tmp_path / "run"
    _write_files(
        worktree_path / "proof",
        [
            "TP-CURRENT_PROOF.json",
            "TP-CURRENT_TRACE.log",
            "TP-CURRENT_PROOF_BUNDLE.json",
            "TP-CURRENT_step_1_CLAUDE_OUTPUT.json",
            "TP-OTHER_PROOF.json",
            "README.md",
        ],
    )

    _copy_proof_artifacts(worktree_path=worktree_path, run_dir=run_dir, tp_id="TP-CURRENT")

    assert sorted(path.name for path in run_dir.iterdir()) == [
        "TP-CURRENT_PROOF.json",
        "TP-CURRENT_PROOF_BUNDLE.json",
        "TP-CURRENT_TRACE.log",
        "TP-CURRENT_step_1_CLAUDE_OUTPUT.json",
    ]


def test_copy_proof_artifacts_returns_current_bundle(tmp_path: Path) -> None:
    worktree_path = tmp_path / "worktree"
    run_dir = tmp_path / "run"
    _write_files(
        worktree_path / "proof",
        [
            "TP-CURRENT_PROOF_BUNDLE.json",
            "TP-OTHER_PROOF_BUNDLE.json",
        ],
    )

    copied_bundle = _copy_proof_artifacts(worktree_path=worktree_path, run_dir=run_dir, tp_id="TP-CURRENT")

    assert copied_bundle == (run_dir / "TP-CURRENT_PROOF_BUNDLE.json").resolve()


def test_cleanup_generated_files_preserves_unrelated_proof_files(tmp_path: Path) -> None:
    worktree_path = tmp_path / "worktree"
    proof_dir = worktree_path / "proof"
    _write_files(
        proof_dir,
        [
            "TP-CURRENT_PROOF.json",
            "TP-CURRENT_TRACE.log",
            "TP-OTHER_PROOF.json",
            "README.md",
        ],
    )

    _cleanup_generated_files(worktree_path, tp_id="TP-CURRENT")

    assert sorted(path.name for path in proof_dir.iterdir()) == [
        "README.md",
        "TP-OTHER_PROOF.json",
    ]
    assert proof_dir.exists()


def test_cleanup_generated_files_removes_empty_proof_dir(tmp_path: Path) -> None:
    worktree_path = tmp_path / "worktree"
    proof_dir = worktree_path / "proof"
    _write_files(
        proof_dir,
        [
            "TP-CURRENT_PROOF.json",
            "TP-CURRENT_PROOF_BUNDLE.json",
        ],
    )

    _cleanup_generated_files(worktree_path, tp_id="TP-CURRENT")

    assert not proof_dir.exists()


def test_cleanup_generated_files_still_removes_series_context(tmp_path: Path) -> None:
    worktree_path = tmp_path / "worktree"
    dopetask_dir = worktree_path / ".dopetask"
    dopetask_dir.mkdir(parents=True)
    (dopetask_dir / "SERIES_CONTEXT.json").write_text("{}\n", encoding="utf-8")

    _cleanup_generated_files(worktree_path, tp_id="TP-CURRENT")

    assert not (dopetask_dir / "SERIES_CONTEXT.json").exists()
    assert not dopetask_dir.exists()
