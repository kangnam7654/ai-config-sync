"""공통 test fixtures."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# sync-timestamps.py는 하이픈 때문에 직접 import 불가 → importlib 사용
_SYNC_PATH = Path(__file__).resolve().parent.parent / "sync-timestamps.py"
_spec = importlib.util.spec_from_file_location("sync_timestamps", _SYNC_PATH)
assert _spec and _spec.loader
sync_timestamps = importlib.util.module_from_spec(_spec)
sys.modules["sync_timestamps"] = sync_timestamps
_spec.loader.exec_module(sync_timestamps)


@pytest.fixture
def sync_env(tmp_path: Path) -> dict:
    """동기화 환경을 tmp_path에 구성."""
    sync_dir = tmp_path / "repo"
    sync_dir.mkdir()
    (sync_dir / "timestamps").mkdir()
    (sync_dir / "openclaw" / "workspace").mkdir(parents=True)
    (sync_dir / "claude-code").mkdir()
    local_ws = tmp_path / "local_workspace"
    local_ws.mkdir()
    local_claude = tmp_path / "local_claude"
    local_claude.mkdir()
    return {
        "sync_dir": sync_dir,
        "local_workspace": local_ws,
        "local_claude": local_claude,
        "ts_dir": sync_dir / "timestamps",
        "hostname": "test-host",
    }


class MockGit:
    """git_cmd와 git_bytes의 응답을 테스트별로 설정."""

    def __init__(self) -> None:
        self._responses: dict[str, tuple[str, int]] = {}
        self._byte_responses: dict[str, tuple[bytes, int]] = {}

    def set_cmd(self, key: str, output: str, rc: int = 0) -> None:
        self._responses[key] = (output, rc)

    def set_bytes(self, key: str, output: bytes, rc: int = 0) -> None:
        self._byte_responses[key] = (output, rc)

    def git_cmd(self, args: list[str], cwd) -> tuple[str, int]:
        key = " ".join(args)
        for pattern, response in self._responses.items():
            if pattern in key:
                return response
        return ("", 1)

    def git_bytes(self, args: list[str], cwd) -> tuple[bytes, int]:
        key = " ".join(args)
        for pattern, response in self._byte_responses.items():
            if pattern in key:
                return response
        return (b"", 1)


@pytest.fixture
def mock_git(monkeypatch) -> MockGit:
    """git_cmd와 git_bytes를 MockGit으로 교체."""
    mg = MockGit()
    monkeypatch.setattr(sync_timestamps, "git_cmd", mg.git_cmd)
    monkeypatch.setattr(sync_timestamps, "git_bytes", mg.git_bytes)
    return mg
