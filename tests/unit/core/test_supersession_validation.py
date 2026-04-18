from dopetask.core.schema import TaskPacket
import pytest

def test_task_packet_self_supersession_refusal():
    data = {
        "id": "TP-SELF",
        "target": "test",
        "steps": [{"id": "S1", "task": "test", "validation": ["true"]}],
        "supersedes": ["TP-SELF"]
    }
    with pytest.raises(ValueError, match="cannot supersede itself"):
        TaskPacket.from_dict(data)

def test_task_packet_valid_supersession():
    data = {
        "id": "TP-NEW",
        "target": "test",
        "steps": [{"id": "S1", "task": "test", "validation": ["true"]}],
        "supersedes": ["TP-OLD"]
    }
    tp = TaskPacket.from_dict(data)
    assert tp.supersedes == ["TP-OLD"]
