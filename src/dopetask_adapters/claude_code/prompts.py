"""Prompt helpers for Claude Code task packet execution."""

from __future__ import annotations

from typing import Any


def build_step_prompt(tp: dict[str, Any], step: dict[str, Any]) -> str:
    """Render a deterministic per-step Claude Code execution prompt."""
    requirements = "\n".join(f"- {item}" for item in step.get("requirements", [])) or "- None"
    validation = "\n".join(f"- {item}" for item in step.get("validation", [])) or "- None"
    expected_files = "\n".join(f"- {item}" for item in step.get("expected_files", [])) or "- None"
    context_files = "\n".join(f"- {item}" for item in step.get("context_files", [])) or "- None"
    commands = "\n".join(f"- {item}" for item in step.get("commands", [])) or "- None"

    return f"""You are executing one deterministic dopeTask Task Packet step through Claude Code.

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

Local shell commands that dopeTask will execute after Claude Code returns:
{commands}

Validation commands that dopeTask will run locally after commands:
{validation}

Rules:
- this is one deterministic dopeTask step
- make only the changes required for this step
- do not commit, push, branch, or mutate unrelated files
- do not claim success in output because local validation is authoritative
- keep edits deterministic and fail-closed
"""
