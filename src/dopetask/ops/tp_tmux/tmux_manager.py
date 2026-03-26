"""Tmux session manager for Task Packet isolation."""

import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class TmuxManager:
    """Provides Python bindings for basic tmux session management."""

    def __init__(self) -> None:
        self._check_tmux_installed()

    def _check_tmux_installed(self) -> None:
        """Verifies that tmux is available on the host system."""
        try:
            subprocess.run(["tmux", "-V"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError("tmux is not installed or not found in PATH.") from e

    def start_session(self, session_name: str, working_dir: Path, command: Optional[str] = None) -> bool:
        """Starts a new detached tmux session."""
        if self.session_exists(session_name):
            logger.warning(f"Tmux session '{session_name}' already exists.")
            return False

        args = ["tmux", "new-session", "-d", "-s", session_name, "-c", str(working_dir)]
        if command:
            args.append(command)

        subprocess.run(args, check=True)
        return True

    def list_sessions(self) -> list[str]:
        """Returns a list of active tmux session names."""
        try:
            result = subprocess.run(["tmux", "ls", "-F", "#S"], capture_output=True, text=True, check=True)
            return result.stdout.strip().split("\n")
        except subprocess.CalledProcessError:
            return []

    def session_exists(self, session_name: str) -> bool:
        """Checks if a tmux session exists."""
        return session_name in self.list_sessions()

    def kill_session(self, session_name: str) -> None:
        """Terminates a tmux session."""
        if self.session_exists(session_name):
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=True)

    def attach_session(self, session_name: str) -> None:
        """Attaches to an existing tmux session (interactive)."""
        if not self.session_exists(session_name):
             raise RuntimeError(f"Session '{session_name}' does not exist.")

        # Note: This will replace the current process
        subprocess.run(["tmux", "attach-session", "-t", session_name])
