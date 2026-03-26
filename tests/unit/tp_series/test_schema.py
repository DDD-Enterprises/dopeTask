"""Schema and parser coverage for JSON Task Packet series fields."""

from __future__ import annotations

import json

from dopetask.core.tp_parser import TPParser


def test_tp_parser_reads_series_and_commit_metadata(tmp_path) -> None:
    packet = tmp_path / "packet.json"
    packet.write_text(
        json.dumps(
            {
                "id": "TPX",
                "target": "series packet",
                "steps": [{"id": "s1", "task": "run", "validation": ["true"]}],
                "depends_on": ["TPA"],
                "series": {
                    "id": "SERIES-X",
                    "base_branch": "main",
                    "parent_tp_id": "TPA",
                    "final_packet": False,
                },
                "commit": {
                    "message": "TPX: commit",
                    "allowlist": ["src/x.txt"],
                    "verify": ["git status --short"],
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
    assert parsed.commit is not None
    assert parsed.commit.allowlist == ["src/x.txt"]

