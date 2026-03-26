"""Aggregator for Task Packet execution proofs."""

import hashlib
import json
import logging
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

class ProofAggregator:
    """Aggregates execution proofs into the canonical Dopetask Proof Bundle format.

    Flow: execution output -> status determination -> archive creation -> final bundle generation.
    Complexity: O(S + F) where S is the number of steps and F is the total size of files to archive.
    """

    def __init__(self, tp_id: str, output_dir: Optional[Path] = None):
        self.tp_id = tp_id
        self.output_dir = output_dir or Path("proof")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _calculate_sha256(self, file_path: Path) -> str:
        """Calculate the SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def create_archive(self, files_to_include: list[Path]) -> dict[str, Any]:
        """Creates a zip archive of the provided files and returns metadata."""
        archive_name = f"{self.tp_id}_PROOF_ARCHIVE.zip"
        archive_path = self.output_dir / archive_name

        manifest_data: dict[str, Any] = {
            "tp_id": self.tp_id,
            "archive_filename": archive_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "included_files": []
        }

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_include:
                if file_path.exists():
                    zipf.write(file_path, file_path.name)
                    manifest_data["included_files"].append({
                        "filename": file_path.name,
                        "sha256": self._calculate_sha256(file_path),
                        "description": f"Artifact generated during {self.tp_id} execution."
                    })

        # Add manifest to zip itself as per standard
        manifest_path = self.output_dir / "PROOF_ARCHIVE_MANIFEST.json"
        try:
            with open(manifest_path, "w") as f:
                json.dump(manifest_data, f, indent=2)

            with zipfile.ZipFile(archive_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(manifest_path, "PROOF_ARCHIVE_MANIFEST.json")
        finally:
            if manifest_path.exists():
                manifest_path.unlink()

        return {
            "present": True,
            "filename": archive_name,
            "sha256": self._calculate_sha256(archive_path)
        }

    def aggregate(self, execution_result: dict[str, Any], artifact_files: list[Path]) -> Path:
        """Translates execution results into a standardized Proof Bundle JSON."""
        steps = execution_result.get("steps", [])

        passed_checks = [s["step_id"] for s in steps if s["validation_passed"]]
        failed_checks = [s["step_id"] for s in steps if not s["validation_passed"]]

        status = "VALIDATED" if not failed_checks else "FAILED"
        if execution_result.get("status") == "PARTIAL":
             status = "PARTIAL"

        summary_result = f"Execution of {self.tp_id} " + ("completed successfully." if status == "VALIDATED" else "encountered failures.")

        key_findings = []
        for step in steps:
            if step["validation_passed"]:
                key_findings.append(f"Step '{step['step_id']}' passed validation.")
            else:
                key_findings.append(f"Step '{step['step_id']}' FAILED.")

        # Generate Archive
        archive_metadata = self.create_archive(artifact_files)

        bundle = {
            "tp_id": self.tp_id,
            "status": status,
            "packet_family": execution_result.get("packet_family", "unknown"),
            "lane": execution_result.get("lane", "agent_exec"),
            "summary": {
                "result": summary_result,
                "key_findings": key_findings,
                "key_caveats": execution_result.get("caveats", [])
            },
            "acceptance_checks": {
                "passed": passed_checks,
                "failed": failed_checks,
                "not_applicable": []
            },
            "validation": {
                "scenario_count": len(steps),
                "scenario_summary": [f"Validated {len(steps)} atomic steps."],
                "coverage_notes": []
            },
            "artifacts": {
                "primary": [f"{self.tp_id}_PROOF_BUNDLE.json"],
                "supporting": [f.name for f in artifact_files],
                "archive": archive_metadata
            },
            "manifest": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "bundle_schema_version": "1.0"
            }
        }

        bundle_path = self.output_dir / f"{self.tp_id}_PROOF_BUNDLE.json"
        with open(bundle_path, "w") as f:
            json.dump(bundle, f, indent=2)

        return bundle_path
