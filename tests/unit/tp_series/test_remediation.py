"""Hardened verification for remediation changes in tp_series logic."""

import subprocess
from pathlib import Path

from dopetask.ops.tp_series.logic import _parse_status_paths, _worktree_context


def _current_branch(repo: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_parse_status_paths_nul_terminated_with_renames():
    # Simulate git status --porcelain -z output
    # Format: XY PATH1\0[PATH2\0]
    # M file1.txt\0
    # A file2.txt\0
    # R old.txt\0new.txt\0
    raw_output = "M  file1.txt\0A  file2.txt\0R  old.txt\0new.txt\0"
    paths = _parse_status_paths(raw_output)
    assert "file1.txt" in paths
    assert "file2.txt" in paths
    assert "new.txt" in paths
    assert "old.txt" not in paths # Source of rename should be skipped
    assert len(paths) == 3

def test_worktree_context_cleanup(tmp_path):
    # Setup a dummy repo
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    (repo / "README.md").write_text("# Test")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)

    base_ref = _current_branch(repo)
    worktree_path = tmp_path / "wt"
    branch = "test-branch"

    # Verify cleanup on success
    with _worktree_context(repo_root=repo, branch=branch, worktree_path=worktree_path, base_ref=base_ref):
        assert worktree_path.exists()
        assert (worktree_path / ".git").exists()

    assert not worktree_path.exists()
    # Check branch exists but worktree is gone
    res = subprocess.run(["git", "worktree", "list"], cwd=repo, capture_output=True, text=True)
    assert str(worktree_path) not in res.stdout

def test_worktree_context_cleanup_on_failure(tmp_path):
    repo = tmp_path / "repo_fail"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    (repo / "README.md").write_text("# Test")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)

    base_ref = _current_branch(repo)
    worktree_path = tmp_path / "wt_fail"
    branch = "test-branch-fail"

    try:
        with _worktree_context(repo_root=repo, branch=branch, worktree_path=worktree_path, base_ref=base_ref):
            assert worktree_path.exists()
            raise RuntimeError("Intentional failure")
    except RuntimeError:
        pass

    # CRITICAL: Worktree must be cleaned up even on failure
    assert not worktree_path.exists()
    res = subprocess.run(["git", "worktree", "list"], cwd=repo, capture_output=True, text=True)
    assert str(worktree_path) not in res.stdout
