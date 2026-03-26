import re
import typing
from pathlib import Path
from typing import NamedTuple

_LEGACY_OPERATOR_BRAND = "TASK" + "X"

OPERATOR_BEGIN_MARKERS: tuple[str, ...] = (
    "<!-- DOPETASK:BEGIN operator_system",
    f"<!-- {_LEGACY_OPERATOR_BRAND}:BEGIN operator_system",
)
OPERATOR_END_MARKERS: tuple[str, ...] = (
    "<!-- DOPETASK:END operator_system -->",
    f"<!-- {_LEGACY_OPERATOR_BRAND}:END operator_system -->",
)


class BlockMatch(NamedTuple):
    start: int
    end: int
    platform: str
    model: str
    hash: str
    content: str

def find_block(text: str) -> typing.Optional[BlockMatch]:
    for begin_marker, end_marker in zip(OPERATOR_BEGIN_MARKERS, OPERATOR_END_MARKERS):
        pattern = (
            re.escape(begin_marker)
            + r" v=1 platform=(.*?) model=(.*?) hash=(.*?) -->\n(.*?)\n"
            + re.escape(end_marker)
        )
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return BlockMatch(
                start=match.start(),
                end=match.end(),
                platform=match.group(1),
                model=match.group(2),
                hash=match.group(3),
                content=match.group(4)
            )
    return None


def inject_block(text: str, content: str, platform: str, model: str, content_hash: str) -> str:
    block = (
        f"<!-- DOPETASK:BEGIN operator_system v=1 platform={platform} model={model} hash={content_hash} -->\n"
        f"{content}\n"
        "<!-- DOPETASK:END operator_system -->"
    )

    existing = find_block(text)
    if existing:
        return text[:existing.start] + block + text[existing.end:]

    if text.strip():
        return text.rstrip() + "\n\n" + block + "\n"
    return block + "\n"


def update_file(path: Path, content: str, platform: str, model: str, content_hash: str) -> bool:
    if path.exists():
        text = path.read_text()
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = ""

    existing = find_block(text)
    if existing and existing.hash == content_hash:
        return False # No change

    new_text = inject_block(text, content, platform, model, content_hash)
    path.write_text(new_text)
    return True
