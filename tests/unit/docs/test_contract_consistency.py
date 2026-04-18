from pathlib import Path
import pytest

@pytest.mark.parametrize('path,needle', [
    ('docs/11_PUBLIC_CONTRACT.md', 'tp series'),
    ('docs/11_PUBLIC_CONTRACT.md', 'SERIES_STATE.json'),
    ('docs/22_WORKFLOW_GUIDE.md', 'tp series exec'),
    ('docs/14_PROJECT_DOCTOR.md', 'strict'),
    ('docs/93_CONTRACT_AUDIT_REPORT.md', 'SUPERSEDED'),
    ('docs/archive/ROOT_ARTIFACTS.md', 'Master Packet'),
    ('docs/10_ARCHITECTURE.md', 'four distinct execution planes'),
])
def test_doc_contains_truth(path, needle):
    text = Path(path).read_text().lower()
    assert needle.lower() in text
