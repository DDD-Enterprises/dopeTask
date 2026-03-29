import json
import zipfile
from pathlib import Path

from jsonschema import validate


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_standard_proof_bundle_example_matches_schema():
    repo_root = _repo_root()
    schema = _load_json(repo_root / "proof" / "standards" / "PROOF_BUNDLE_SCHEMA.json")
    example = _load_json(repo_root / "proof" / "standards" / "PROOF_BUNDLE_EXAMPLE.json")

    validate(example, schema)


def test_standard_archive_manifest_example_matches_schema():
    repo_root = _repo_root()
    schema = _load_json(repo_root / "proof" / "standards" / "PROOF_ARCHIVE_MANIFEST_SCHEMA.json")
    example = _load_json(repo_root / "proof" / "standards" / "PROOF_ARCHIVE_EXAMPLE_MANIFEST.json")

    validate(example, schema)


def test_checked_in_proof_bundles_match_standard_schema():
    repo_root = _repo_root()
    schema = _load_json(repo_root / "proof" / "standards" / "PROOF_BUNDLE_SCHEMA.json")
    bundle_paths = sorted((repo_root / "proof").glob("*_PROOF_BUNDLE.json"))
    assert bundle_paths, "expected checked-in proof bundles under /proof"

    for bundle_path in bundle_paths:
        bundle = _load_json(bundle_path)
        validate(bundle, schema)


def test_checked_in_archive_manifests_match_standard_schema():
    repo_root = _repo_root()
    schema = _load_json(repo_root / "proof" / "standards" / "PROOF_ARCHIVE_MANIFEST_SCHEMA.json")
    archive_paths = sorted((repo_root / "proof").glob("*_PROOF_ARCHIVE.zip"))
    assert archive_paths, "expected checked-in proof archives under /proof"

    for archive_path in archive_paths:
        with zipfile.ZipFile(archive_path) as archive:
            manifest = json.loads(archive.read("PROOF_ARCHIVE_MANIFEST.json"))
        validate(manifest, schema)
