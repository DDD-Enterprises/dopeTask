"""CLI registration for dopetask tmux commands."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from dopetask.ops.tp_tmux.tmux_manager import TmuxManager

console = Console()

def register(cli: typer.Typer) -> None:
    """Attach tmux group to the main CLI."""

    tmux_app = typer.Typer(help="Manage Task Packet execution in tmux sessions.")
    cli.add_typer(tmux_app, name="tmux")

    @tmux_app.command("ls")
    def tmux_ls() -> None:
        """List active TP tmux sessions."""
        try:
            manager = TmuxManager()
            sessions = manager.list_sessions()

            if not sessions or (len(sessions) == 1 and sessions[0] == ""):
                console.print("[yellow]No active tmux sessions found.[/yellow]")
                return

            table = Table(title="Active TP Tmux Sessions")
            table.add_column("Session Name", style="cyan")

            for s in sessions:
                if s:
                    table.add_row(s)

            console.print(table)
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(1) from exc

    @tmux_app.command("start")
    def tmux_start(
        tp_id: str = typer.Argument(..., help="Task Packet ID for the session name."),
        command: str = typer.Option(None, "--cmd", help="Command to run in the session."),
    ) -> None:
        """Start a new detached tmux session for a Task Packet."""
        try:
            manager = TmuxManager()
            session_name = f"tp-{tp_id.lower()}"

            if manager.start_session(session_name, Path.cwd(), command):
                console.print(f"[green]Started tmux session:[/green] {session_name}")
                console.print(f"Run 'dopetask tmux attach {tp_id}' to join.")
            else:
                console.print(f"[yellow]Session '{session_name}' already exists.[/yellow]")
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(1) from exc

    @tmux_app.command("attach")
    def tmux_attach(
        tp_id: str = typer.Argument(..., help="Task Packet ID to attach to."),
    ) -> None:
        """Attach to an existing TP tmux session."""
        try:
            manager = TmuxManager()
            session_name = f"tp-{tp_id.lower()}"
            manager.attach_session(session_name)
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(1) from exc

    @tmux_app.command("kill")
    def tmux_kill(
        tp_id: str = typer.Argument(..., help="Task Packet ID to kill."),
    ) -> None:
        """Terminate a TP tmux session."""
        try:
            manager = TmuxManager()
            session_name = f"tp-{tp_id.lower()}"
            manager.kill_session(session_name)
            console.print(f"[red]Killed tmux session:[/red] {session_name}")
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(1) from exc
