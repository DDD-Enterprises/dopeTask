"""CLI registration for dopetask tp exec command."""

from __future__ import annotations

import json
import shlex
from pathlib import Path

import typer

from dopetask.core.tp_parser import TPNormalizer, TPParser
from dopetask.guard.governed_execution import load_governed_task_packet
from dopetask.ops.tp_exec.engine import execute_task_packet, resolve_governed_admission
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
            help="Agent profile: gemini, codex, or claude_code.",
        ),
        model: str | None = typer.Option(
            None,
            "--model",
            help="Optional explicit model override for the selected agent.",
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
        governed: bool = typer.Option(
            False,
            "--governed/--no-governed",
            help=(
                "Require C0-R2 GOVERNED_MODE admission (MacroExecutionAuthorityRefV2 + "
                "DCPRouteAuthorization) instead of LEGACY_LOCAL_MODE. build_route_plan is "
                "never called in this mode."
            ),
        ),
        grant: Path | None = typer.Option(
            None,
            "--grant",
            exists=True,
            file_okay=True,
            dir_okay=False,
            help="MacroExecutionAuthorityRefV2 grant JSON path (required with --governed).",
        ),
        dcp_route_authorization: Path | None = typer.Option(
            None,
            "--dcp-route-authorization",
            exists=True,
            file_okay=True,
            dir_okay=False,
            help="DCPRouteAuthorization JSON path (required with --governed).",
        ),
    ) -> None:
        """Execute a Task Packet using a specific agent profile."""
        try:
            resolved_tp_file = tp_file.resolve()
            # On the governed path the packet is read and parsed through the
            # shared governed loader, so a malformed/unreadable packet refuses
            # as a GovernedAdmissionError with a stable reason rather than
            # surfacing a raw parse error through the generic handler below.
            # (A missing or unreadable file is already pre-empted one layer up
            # by the `exists=True` Click argument, which also implies
            # `readable=True`; that legacy behaviour is left untouched.)
            packet_raw: bytes | None = None
            if governed:
                packet_raw, tp = load_governed_task_packet(resolved_tp_file)
            else:
                tp = TPParser.parse_file(resolved_tp_file)

            if use_tmux:
                manager = TmuxManager()
                session_name = f"tp-{tp.id.lower()}"
                # Construct command to run itself without --tmux
                command_parts = ["dopetask", "tp", "exec", str(resolved_tp_file), "--agent", agent]
                if model:
                    command_parts.extend(["--model", model])
                if governed:
                    command_parts.append("--governed")
                    if grant is not None:
                        command_parts.extend(["--grant", str(grant.resolve())])
                    if dcp_route_authorization is not None:
                        command_parts.extend(
                            ["--dcp-route-authorization", str(dcp_route_authorization.resolve())]
                        )
                cmd = shlex.join(command_parts)
                if manager.start_session(session_name, Path.cwd(), cmd):
                    typer.echo(f"Spawned execution in tmux session: {session_name}")
                    typer.echo(f"Run 'dopetask tmux attach {tp.id}' to monitor.")
                    raise typer.Exit(0)
                else:
                    typer.echo(f"Failed to start tmux session '{session_name}'. It might already exist.", err=True)
                    raise typer.Exit(1)

            if dry_run:
                if governed:
                    # Admission must be evaluated before a compiled governed
                    # execution is ever claimed, even in dry-run.
                    resolve_governed_admission(
                        resolved_tp_file,
                        tp,
                        agent=agent,
                        model=model,
                        grant_path=grant,
                        dcp_route_authorization_path=dcp_route_authorization,
                        packet_raw=packet_raw,
                    )
                typer.echo(f"--- Compiled Profile: {agent} ---")
                typer.echo(json.dumps(TPNormalizer.compile(tp, agent), indent=2))
                raise typer.Exit(0)

            bundle_path = execute_task_packet(
                resolved_tp_file,
                agent=agent,
                model=model,
                governed=governed,
                grant_path=grant,
                dcp_route_authorization_path=dcp_route_authorization,
            )
            typer.echo(f"Success! Canonical Proof Bundle written to: {bundle_path}")
            typer.echo("Audit archive created in same directory.")

        except typer.Exit:
            raise
        except ValueError as exc:
            typer.echo(f"Compilation Failed: {exc}", err=True)
            raise typer.Exit(1) from exc
        except Exception as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(1) from exc
