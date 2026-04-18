from dopetask.core.schema import TaskPacket
from dopetask.core.compilers.gemini import GeminiCompiler
import pytest

def test_gemini_rejects_missing_pal():
    data = {
        "id": "TP-PAL",
        "target": "test",
        "steps": [{"id": "S1", "task": "test", "validation": ["true"]}]
    }
    tp = TaskPacket.from_dict(data)
    compiler = GeminiCompiler()
    with pytest.raises(ValueError, match="requires a valid and enabled pal_chain"):
        compiler.compile(tp)

def test_gemini_rejects_empty_pal_steps():
    data = {
        "id": "TP-PAL",
        "target": "test",
        "steps": [{"id": "S1", "task": "test", "validation": ["true"]}],
        "pal_chain": {"enabled": True, "steps": []}
    }
    tp = TaskPacket.from_dict(data)
    compiler = GeminiCompiler()
    with pytest.raises(ValueError, match="requires non-empty pal_chain.steps"):
        compiler.compile(tp)

def test_gemini_requires_mapping():
    data = {
        "id": "TP-PAL",
        "target": "test",
        "steps": [{"id": "S1", "task": "t1", "validation": ["true"]}, {"id": "S2", "task": "t2", "validation": ["true"]}],
        "pal_chain": {"enabled": True, "steps": ["only one pal step"]}
    }
    tp = TaskPacket.from_dict(data)
    compiler = GeminiCompiler()
    with pytest.raises(ValueError, match="Each execution step must have a corresponding PAL step mapping"):
        compiler.compile(tp)
