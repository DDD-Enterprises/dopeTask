import json
import os
import shutil
import subprocess
from pathlib import Path
import pytest
from dopetask.ops.tp_exec.engine import execute_task_packet

@pytest.mark.skipif(not shutil.which('codex'), reason='Codex binary not found')
def test_codex_live_e2e_success(tmp_path: Path):
    pass
