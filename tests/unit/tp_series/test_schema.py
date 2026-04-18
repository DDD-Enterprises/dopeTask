"""Schema and parser coverage for JSON Task Packet series fields."""

from __future__ import annotations

import json

from dopetask.core.tp_parser import TPParser
from dopetask.schemas.validator import validate_data


def test_tp_parser_reads_series_and_commit_metadata(tmp_path) -> None:
    packet = tmp_path / "packet.json"
    packet.write_text(
        json.dumps(
            {
                "id": "TPX",
                "target": "series packet",
                "steps": [{"id": "s1", "task": "run", "validation": ["true"]}],
                "repo_binding": {
                    "project_id": "dopetask.core",
                    "repo_marker": ".dopetaskroot",
                    "origin_hint": "git@github.com:example/dopetask.git",
                    "require_identity_match": True,
                },
                "depends_on": ["TPA"],
                "series": {
                    "id": "SERIES-X",
                    "base_branch": "main",
                    "parent_tp_id": "TPA",
                    "final_packet": False,
                },
                "execution": {
                    "agent": "gemini",
                    "branch": "series/SERIES-X/TPX",
                },
                "pal_chain": {
                    "enabled": True,
                    "steps": ["analysis"],
                },
                "commit": {
                    "message": "TPX: commit",
                    "allowlist": ["src/x.txt"],
                    "verify": ["git status --short"],
                },
                "pr": {
                    "title": "Series X",
                    "body": "Ready for review.",
                    "base": "main",
                },
            }
        ),
        encoding="utf-8",
    )

    parsed = TPParser.parse_file(packet)

    assert parsed.depends_on == ["TPA"]
    assert parsed.series is not None
    assert parsed.series.id == "SERIES-X"
    assert parsed.series.parent_tp_id == "TPA"
    assert parsed.repo_binding is not None
    assert parsed.repo_binding.project_id == "dopetask.core"
    assert parsed.execution is not None
    assert parsed.execution.branch == "series/SERIES-X/TPX"
    assert parsed.commit is not None
    assert parsed.commit.allowlist == ["src/x.txt"]
    assert parsed.pr is not None
    assert parsed.pr["title"] == "Series X"


def test_strict_task_packet_schema_accepts_non_gemini_with_pal_chain() -> None:
    packet = {
        "id": "TPX",
        "project": "dopetask",
        "target": "strict packet",
        "invariants": ["keep repo identity matched"],
        "repo_binding": {
            "project_id": "dopetask.core",
            "repo_marker": ".dopetaskroot",
            "require_identity_match": True,
        },
        "series": {
            "id": "SERIES-X",
            "base_branch": "main",
            "parent_tp_id": None,
            "final_packet": True,
        },
        "execution": {
            "agent": "codex",
            "branch": "series/SERIES-X/TPX",
        },
        "commit": {
            "message": "TPX: commit",
            "allowlist": ["src/x.txt"],
            "verify": ["git status --short"],
        },
        "pr": {
            "title": "SERIES-X: strict packet",
            "body": "Ready for review.",
            "base": "main",
        },
        "pal_chain": {
            "enabled": False,
            "steps": ["analysis"],
        },
        "steps": [
            {
                "id": "s1",
                "task": "run",
                "validation": ["true"],
            }
        ],
    }

    ok, errors = validate_data(packet, "task_packet.strict", strict=False)

    assert ok is True
    assert errors == []


def test_strict_task_packet_schema_requires_enabled_pal_chain_for_gemini() -> None:
    packet = {
        "id": "TPX",
        "project": "dopetask",
        "target": "strict packet",
        "invariants": ["keep repo identity matched"],
        "repo_binding": {
            "project_id": "dopetask.core",
            "repo_marker": ".dopetaskroot",
            "require_identity_match": True,
        },
        "series": {
            "id": "SERIES-X",
            "base_branch": "main",
            "parent_tp_id": None,
            "final_packet": True,
        },
        "execution": {
            "agent": "gemini",
            "branch": "series/SERIES-X/TPX",
        },
        "commit": {
            "message": "TPX: commit",
            "allowlist": ["src/x.txt"],
            "verify": ["git status --short"],
        },
        "pr": {
            "title": "SERIES-X: strict packet",
            "body": "Ready for review.",
            "base": "main",
        },
        "pal_chain": {
            "enabled": False,
            "steps": ["analysis"],
        },
        "steps": [
            {
                "id": "s1",
                "task": "run",
                "validation": ["true"],
            }
        ],
    }

    ok, errors = validate_data(packet, "task_packet.strict", strict=False)

    assert ok is False
    assert any("pal_chain" in error for error in errors)


def test_strict_task_packet_schema_requires_execution_and_commit_verify() -> None:
    packet = {
        "id": "TPX",
        "project": "dopetask",
        "target": "strict packet",
        "invariants": ["keep repo identity matched"],
        "repo_binding": {
            "project_id": "dopetask.core",
            "repo_marker": ".dopetaskroot",
            "require_identity_match": True,
        },
        "series": {
            "id": "SERIES-X",
            "base_branch": "main",
            "parent_tp_id": None,
            "final_packet": True,
        },
        "commit": {
            "message": "TPX: commit",
            "allowlist": ["src/x.txt"],
            "verify": [],
        },
        "pr": {
            "title": "SERIES-X: strict packet",
            "body": "Ready for review.",
            "base": "main",
        },
        "steps": [
            {
                "id": "s1",
                "task": "run",
                "validation": ["true"],
            }
        ],
    }

    ok, errors = validate_data(packet, "task_packet.strict", strict=False)

    assert ok is False
    assert any("execution" in error for error in errors)
    assert any("verify" in error for error in errors)
