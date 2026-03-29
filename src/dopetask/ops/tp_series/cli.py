"""CLI surface for DAG-aware TP series commands."""

from __future__ import annotations

import typing
from pathlib import Path

import typer

from dopetask.ops.tp_series.logic import (
    exec_series_packet,
    finalize_series,
    get_series_status,
    import_series_packet,
)

app = typer.Typer(
    name="series",
    help="JSON Task Packet series commands",
    no_args_is_help=True,
)


@app.command("import")
def import_cmd(
    source_file: typing.Optional[Path] = typer.Option(
        None, "--file", "-f", help="Source JSON file (if not using clipboard)."
    ),
    out_dir: typing.Optional[Path] = typer.Option(None, "--out-dir", help="Output directory for imported packet."),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing packet file if it already exists."),
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Allow updating/replacing an already-recorded packet safely."
    ),
    clipboard_backend: str = typer.Option(
        "auto",
        "--clipboard-backend",
        help="Clipboard backend: auto, pbpaste, wl-paste, xclip, or xsel.",
    ),
    repo: typing.Optional[Path] = typer.Option(None, "--repo", help="Repository path."),
) -> None:
    """Import a JSON Task Packet into the series workflow."""
    try:
        result = import_series_packet(
            out_dir=out_dir,
            source_file=source_file,
            force=force,
            overwrite=overwrite,
            clipboard_backend=clipboard_backend,
            repo=repo,
        )
    except Exception as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"repo_root={result.repo_root}")
    typer.echo(f"series_id={result.series_id}")
    typer.echo(f"tp_id={result.tp_id}")
    typer.echo(f"packet_path={result.packet_path}")
    typer.echo(f"validation={result.validation}")
    typer.echo(f"next_command=dopetask tp series exec {result.packet_path} --agent gemini")
    typer.echo(result.message)


@app.command("exec")
def exec_cmd(
    tp_file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, metavar="TP_FILE"),
    agent: str = typer.Option("gemini", "--agent", help="Agent profile: gemini, codex, or vibe."),
    force: bool = typer.Option(
        False, "--force", help="Force execution even if branch/worktree already exists (destructive)."
    ),
    repo: typing.Optional[Path] = typer.Option(None, "--repo", help="Repository path."),
) -> None:
    """Execute a JSON Task Packet inside a DAG-aware series workflow."""
    try:
        result = exec_series_packet(tp_file=tp_file, agent=agent, force=force, repo=repo)
    except Exception as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"repo_root={result.repo_root}")
    typer.echo(f"series_id={result.series_id}")
    typer.echo(f"tp_id={result.tp_id}")
    typer.echo(f"branch={result.branch}")
    typer.echo(f"worktree_path={result.worktree_path}")
    typer.echo(f"run_dir={result.run_dir}")
    if result.proof_bundle is not None:
        typer.echo(f"proof_bundle={result.proof_bundle}")
    typer.echo(result.message)


@app.command("cleanup")
def cleanup_cmd(
    series_id: str = typer.Argument(..., metavar="SERIES_ID"),
    packet_id: typing.Optional[str] = typer.Option(None, "--packet-id", help="Optional specific packet to clean."),
    force: bool = typer.Option(False, "--force", help="Clean up even if status is completed."),
    repo: typing.Optional[Path] = typer.Option(None, "--repo", help="Repository path."),
) -> None:
    """Clean up stale worktrees and branches for a series."""
    from dopetask.ops.tp_series.logic import cleanup_series_artifacts, resolve_repo_root

    repo_root = resolve_repo_root(repo)
    try:
        cleaned = cleanup_series_artifacts(
            repo_root=repo_root,
            series_id=series_id,
            packet_id=packet_id,
            force=force,
        )
        if not cleaned:
            typer.echo("Nothing to clean.")
        for item in cleaned:
            typer.echo(f"cleaned: {item}")
    except Exception as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


@app.command("status")
def status_cmd(
    series_id: str = typer.Argument(..., metavar="SERIES_ID"),
    repo: typing.Optional[Path] = typer.Option(None, "--repo", help="Repository path."),
) -> None:
    """Show the authoritative series state."""
    try:
        payload = get_series_status(series_id=series_id, repo=repo)
    except Exception as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"repo_root={payload['repo_root']}")
    typer.echo(f"series_id={payload['series_id']}")
    typer.echo(f"base_branch={payload['base_branch']}")
    counts = payload["counts"]
    typer.echo(f"running={counts['running']}")
    typer.echo(f"completed={counts['completed']}")
    typer.echo(f"failed={counts['failed']}")
    typer.echo(f"state_path={payload['state_path']}")
    for packet_id, packet in sorted(payload["packets"].items()):
        typer.echo(
            f"packet={packet_id} status={packet.get('status')} branch={packet.get('branch')} "
            f"final={str(packet.get('final_packet')).lower()}"
        )
    pr = payload.get("pr")
    if isinstance(pr, dict):
        typer.echo(f"pr_url={pr.get('url', '')}")
        typer.echo(f"pr_state={pr.get('state', '')}")


@app.command("finalize")
def finalize_cmd(
    series_id: str = typer.Argument(..., metavar="SERIES_ID"),
    title: str = typer.Option(..., "--title", help="Pull request title."),
    body: typing.Optional[str] = typer.Option(None, "--body", help="Pull request body text."),
    body_file: typing.Optional[Path] = typer.Option(None, "--body-file", help="Pull request body file path."),
    repo: typing.Optional[Path] = typer.Option(None, "--repo", help="Repository path."),
) -> None:
    """Open the single PR for a completed TP series."""
    try:
        payload = finalize_series(series_id=series_id, title=title, body=body, body_file=body_file, repo=repo)
    except Exception as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"repo_root={payload['repo_root']}")
    typer.echo(f"series_id={payload['series_id']}")
    typer.echo(f"final_tp_id={payload['final_tp_id']}")
    typer.echo(f"branch={payload['branch']}")
    typer.echo(f"base_branch={payload['base_branch']}")
    typer.echo(f"url={payload.get('url', '')}")
    typer.echo(f"state={payload.get('state', '')}")
    typer.echo(f"mergeStateStatus={payload.get('mergeStateStatus', '')}")
