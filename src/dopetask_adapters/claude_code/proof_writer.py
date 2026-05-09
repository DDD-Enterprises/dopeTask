"""Proof writer for Claude Code task packet execution."""

from __future__ import annotations

from typing import Any, Optional

from dopetask_adapters.gemini.proof_writer import ProofWriter as BaseProofWriter


class ProofWriter(BaseProofWriter):
    """Write Claude proof metadata exactly as provided by the executor."""

    def write(
        self,
        tp_id: str,
        steps: list[dict[str, Any]],
        *,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        return super().write(tp_id, steps, metadata=dict(metadata) if metadata else None)

__all__ = ["ProofWriter"]
