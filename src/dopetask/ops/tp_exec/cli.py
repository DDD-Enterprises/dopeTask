"""CLI registration for dopetask tp exec command."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from dopetask.core.tp_parser import TPNormalizer, TPParser
from dopetask_adapters.gemini.executor import GeminiExecutor
from dopetask.obs.proof_aggregator import ProofAggregator
from dopetask.ops.tp_tmux.tmux_manager import TmuxManager

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
        use_tmux: bool = typer.Option(
            False,
            "--tmux",
            help="Run execution inside an isolated tmux session.",
        ),
    ) -> None:
        """Execute a Task Packet using a specific agent profile."""
        try:
            # 1. Parse generic TP
            tp = TPParser.parse_file(tp_file)
            
            if use_tmux:
                manager = TmuxManager()
                session_name = f"tp-{tp.id.lower()}"
                # Construct command to run itself without --tmux
                cmd = f"dopetask tp exec {tp_file} --agent {agent}"
                if manager.start_session(session_name, Path.cwd(), cmd):
                    typer.echo(f"Spawned execution in tmux session: {session_name}")
                    typer.echo(f"Run 'dopetask tmux attach {tp.id}' to monitor.")
                    raise typer.Exit(0)
                else:
                    typer.echo(f"Failed to start tmux session '{session_name}'. It might already exist.", err=True)
                    raise typer.Exit(1)

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
            raw_proof_path = Path(executor.run_tp(compiled_tp))
            
            # 4. Aggregate Proofs
            typer.echo(f"Aggregating proofs for {tp.id}...")
            aggregator = ProofAggregator(tp.id)
            
            with open(raw_proof_path, "r") as f:
                execution_result = json.load(f)
            
            # Identify artifacts to include in archive
            artifact_files = [raw_proof_path, tp_file]
            for step in execution_result.get("steps", []):
                for f in step.get("files_created", []):
                    artifact_files.append(Path(f))
            
            bundle_path = aggregator.aggregate(execution_result, artifact_files)
            
            typer.echo(f"Success! Canonical Proof Bundle written to: {bundle_path}")
            typer.echo(f"Audit archive created in same directory.")
            
        except typer.Exit:
            raise
        except ValueError as exc:
            typer.echo(f"Compilation Failed: {exc}", err=True)
            raise typer.Exit(1) from exc
        except Exception as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(1) from exc
