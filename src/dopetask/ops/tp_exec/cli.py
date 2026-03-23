"""CLI registration for dopetask tp exec command."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from dopetask.core.tp_parser import TPNormalizer, TPParser
from dopetask_adapters.gemini.executor import GeminiExecutor

def register(tp_app: typer.Typer) -> None:
    """Attach tp exec command to the tp group."""

    @tp_app.command("exec")
    def tp_exec(
        tp_file: Path = typer.Argument(
            ...,
            exists=True,
            file_okay=True,
            dir_okay=False,
            help="Generic Task Packet JSON file.",
        ),
        agent: str = typer.Option(
            "gemini",
            "--agent",
            help="Agent profile: gemini, codex, or vibe.",
        ),
        dry_run: bool = typer.Option(
            False,
            "--dry-run",
            help="Compile and show prompts without executing.",
        ),
    ) -> None:
        """Execute a Task Packet using a specific agent profile."""
        try:
            # 1. Parse generic TP
            tp = TPParser.parse_file(tp_file)
            
            # 2. Compile to agent profile
            compiled_tp = TPNormalizer.compile(tp, agent)
            
            if dry_run:
                typer.echo(f"--- Compiled Profile: {agent} ---")
                typer.echo(json.dumps(compiled_tp, indent=2))
                raise typer.Exit(0)
                
            # 3. Instantiate and run Executor
            if agent == "gemini":
                executor = GeminiExecutor()
            else:
                typer.echo(f"Agent profile '{agent}' not yet fully implemented in executor.", err=True)
                raise typer.Exit(1)
                
            typer.echo(f"Executing TP: {tp.id} (agent={agent})...")
            proof_file = executor.run_tp(compiled_tp)
            
            typer.echo(f"Success! Proof written to: {proof_file}")
            
        except typer.Exit:
            raise
        except ValueError as exc:
            typer.echo(f"Compilation Failed: {exc}", err=True)
            raise typer.Exit(1) from exc
        except Exception as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(1) from exc
