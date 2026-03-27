import json
from pathlib import Path
from dopetask.obs.proof_aggregator import ProofAggregator

def test_proof_aggregator_standard_output(tmp_path):
    """Verify that ProofAggregator generates a bundle matching the authority contract."""
    agg = ProofAggregator(tp_id="TP-TEST-001", output_dir=tmp_path)
    
    execution_result = {
        "steps": [
            {"step_id": "s1", "validation_passed": True},
            {"step_id": "s2", "validation_passed": False}
        ],
        "packet_family": "test_family",
        "lane": "test_lane",
        "status": "FAILED"
    }
    
    artifact_files = [tmp_path / "test_artifact.txt"]
    artifact_files[0].write_text("dummy content")
    
    bundle_path = agg.aggregate(execution_result, artifact_files)
    
    assert bundle_path.exists()
    bundle = json.loads(bundle_path.read_text())
    
    # Contract: No 'decision' or 'dopetask' blocks in standard output
    assert "decision" not in bundle
    assert "dopetask" not in bundle
    
    # Contract: Standard required sections
    expected_sections = {
        "tp_id", "status", "packet_family", "lane", 
        "summary", "acceptance_checks", "validation", 
        "artifacts", "manifest"
    }
    assert set(bundle.keys()) == expected_sections
    
    # Contract: Archive metadata uses 'filename'
    assert "filename" in bundle["artifacts"]["archive"]
    assert bundle["artifacts"]["archive"]["filename"] == "TP-TEST-001_PROOF_ARCHIVE.zip"
    
    # Contract: Validation scenario count matches steps
    assert bundle["validation"]["scenario_count"] == 2

def test_proof_aggregator_archive_manifest(tmp_path):
    """Verify the internal archive manifest matches the authority contract."""
    agg = ProofAggregator(tp_id="TP-TEST-002", output_dir=tmp_path)
    
    file1 = tmp_path / "file1.json"
    file1.write_text("{}")
    
    # create_archive is called during aggregate, but we can test it directly if needed
    # for now, we'll check the side effect of create_archive when called via aggregate
    agg.aggregate({"steps": []}, [file1])
    
    # The manifest is temporary and deleted after zip creation in ProofAggregator.
    # We should verify the contents of the zip or the logic that generates it.
    # ProofAggregator.create_archive returns the metadata that goes into the bundle.
    meta = agg.create_archive([file1])
    
    assert meta["present"] is True
    assert meta["filename"] == "TP-TEST-002_PROOF_ARCHIVE.zip"
    assert "sha256" in meta
