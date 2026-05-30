"""Tests for the BuzzHeavier uploader."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def buzzheavier_module(monkeypatch):
    """Import BuzzHeavier uploader with stubbed bot package."""
    bot_pkg = ModuleType("bot")
    bot_pkg.__path__ = []  # mark as package so submodule imports work
    config_pkg = ModuleType("bot.core")
    config_pkg.__path__ = []
    config_manager = ModuleType("bot.core.config_manager")

    class Config:
        BUZZHEAVIER_ACCOUNT_ID = ""

    config_manager.Config = Config
    helper_pkg = ModuleType("bot.helper")
    helper_pkg.__path__ = []
    mlu_pkg = ModuleType("bot.helper.mirror_leech_utils")
    # Real on-disk path so importlib can locate
    # ``buzzheavier_uploader`` relative to the package.
    mlu_pkg.__path__ = [
        str(Path(__file__).resolve().parent.parent / "bot" / "helper" / "mirror_leech_utils")
    ]

    monkeypatch.setitem(sys.modules, "bot", bot_pkg)
    monkeypatch.setitem(sys.modules, "bot.core", config_pkg)
    monkeypatch.setitem(sys.modules, "bot.core.config_manager", config_manager)
    monkeypatch.setitem(sys.modules, "bot.helper", helper_pkg)
    monkeypatch.setitem(sys.modules, "bot.helper.mirror_leech_utils", mlu_pkg)

    sys.modules.pop(
        "bot.helper.mirror_leech_utils.buzzheavier_uploader", None
    )
    return importlib.import_module(
        "bot.helper.mirror_leech_utils.buzzheavier_uploader"
    )


def _make_listener():
    return SimpleNamespace(
        is_cancelled=False,
        size=0,
        on_upload_complete=AsyncMock(),
        on_upload_error=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_upload_walks_directory(buzzheavier_module, tmp_path, monkeypatch):
    file_a = tmp_path / "a.bin"
    file_b = tmp_path / "sub" / "b.bin"
    file_b.parent.mkdir()
    file_a.write_bytes(b"a" * 1024)
    file_b.write_bytes(b"b" * 2048)

    listener = _make_listener()
    listener.size = file_a.stat().st_size + file_b.stat().st_size

    uploader = buzzheavier_module.BuzzHeavierUploader(listener, str(tmp_path))

    upload_calls: list[str] = []

    async def fake_upload_one(self, client, file_path):
        upload_calls.append(os.path.basename(file_path))
        self._processed_bytes += os.path.getsize(file_path)
        return f"https://buzzheavier.com/{os.path.basename(file_path)}"

    monkeypatch.setattr(
        buzzheavier_module.BuzzHeavierUploader,
        "_upload_one",
        fake_upload_one,
    )

    await uploader.upload()

    assert sorted(upload_calls) == ["a.bin", "b.bin"]
    listener.on_upload_complete.assert_awaited()
    args = listener.on_upload_complete.await_args.args
    # link, files_dict, total_files, mime_type
    assert args[0].startswith("https://buzzheavier.com/")
    assert len(args[1]) == 2
    assert args[2] == 2
    assert args[3] == "BuzzHeavier"


@pytest.mark.asyncio
async def test_upload_handles_empty_path(buzzheavier_module, tmp_path):
    listener = _make_listener()
    uploader = buzzheavier_module.BuzzHeavierUploader(
        listener, str(tmp_path)
    )
    await uploader.upload()
    listener.on_upload_error.assert_awaited()
    listener.on_upload_complete.assert_not_awaited()


@pytest.mark.asyncio
async def test_upload_aborts_when_cancelled(
    buzzheavier_module, tmp_path, monkeypatch
):
    file_a = tmp_path / "a.bin"
    file_a.write_bytes(b"a" * 16)
    listener = _make_listener()
    listener.size = file_a.stat().st_size

    uploader = buzzheavier_module.BuzzHeavierUploader(listener, str(tmp_path))

    async def fake_upload_one(self, client, file_path):
        # Simulate cancellation mid-loop after the first file.
        listener.is_cancelled = True
        return f"https://buzzheavier.com/{os.path.basename(file_path)}"

    monkeypatch.setattr(
        buzzheavier_module.BuzzHeavierUploader,
        "_upload_one",
        fake_upload_one,
    )

    # Add a second file so the cancelled branch runs on iteration 2.
    (tmp_path / "b.bin").write_bytes(b"b" * 16)
    await uploader.upload()

    listener.on_upload_error.assert_awaited()
    listener.on_upload_complete.assert_not_awaited()


def test_status_interface_exposed(buzzheavier_module, tmp_path):
    listener = _make_listener()
    uploader = buzzheavier_module.BuzzHeavierUploader(listener, str(tmp_path))
    # Properties used by BuzzHeavierStatus.
    assert hasattr(uploader, "processed_bytes")
    assert isinstance(uploader.processed_bytes, int)
    assert hasattr(uploader, "speed")
    # Speed is computed lazily; first call returns 0.0 because
    # processed_bytes is still 0.
    assert uploader.speed == 0.0


def test_auth_headers_uses_config(buzzheavier_module, monkeypatch):
    monkeypatch.setattr(
        buzzheavier_module.Config, "BUZZHEAVIER_ACCOUNT_ID", "abc-123"
    )
    headers = buzzheavier_module._auth_headers()
    assert headers["Authorization"] == "Bearer abc-123"


def test_auth_headers_empty_when_unset(buzzheavier_module, monkeypatch):
    monkeypatch.setattr(
        buzzheavier_module.Config, "BUZZHEAVIER_ACCOUNT_ID", ""
    )
    headers = buzzheavier_module._auth_headers()
    assert "Authorization" not in headers
