"""Prompt helpers for Codex task packet execution."""

from __future__ import annotations

from typing import Any


def build_step_prompt(tp: dict[str, Any], step: dict[str, Any]) -> str:
    """Render a deterministic per-step Codex execution prompt."""
    requirements = "\n".join(f"- {item}" for item in step.get("requirements", [])) or "- None"
    validation = "\n".join(f"- {item}" for item in step.get("validation", [])) or "- None"
    expected_files = "\n".join(f"- {item}" for item in step.get("expected_files", [])) or "- None"
    context_files = "\n".join(f"- {item}" for item in step.get("context_files", [])) or "- None"
    commands = "\n".join(f"- {item}" for item in step.get("commands", [])) or "- None"

    return f"""You are executing one deterministic dopeTask Task Packet step.

Task Packet:
- id: {tp.get("id", "UNKNOWN")}
- project: {tp.get("project", "dopetask")}
- target: {tp.get("target", "UNKNOWN")}

Step:
- id: {step.get("id", "UNKNOWN")}
- task: {step.get("task", "")}

Requirements:
{requirements}

Context files to inspect before editing:
{context_files}

Expected files for this step:
{expected_files}

Local shell commands that dopeTask will execute after your edits:
{commands}

Validation commands that dopeTask will run locally after your edits:
{validation}

Rules:
- make only the changes required for this step
- do not claim success in output; local validation is authoritative
- keep edits deterministic and fail-closed
- do not delete unrelated files
"""
