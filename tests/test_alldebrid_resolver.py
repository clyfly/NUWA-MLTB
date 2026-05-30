"""Tests for the AllDebrid resolver."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType
from unittest.mock import patch

import pytest


@pytest.fixture
def alldebrid_module(monkeypatch):
    """Import ``alldebrid_resolver`` with the bot package stubs in place.

    The real ``bot/__init__.py`` performs side effects (reads env, opens
    sockets) we do not want during unit tests. We pre-register a
    minimal stub so the resolver module imports cleanly.
    """
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent

    # Stub the top-level ``bot`` package and its sub-modules used by the
    # resolver. This keeps tests free of Telegram/Pyrogram side effects.
    bot_pkg = ModuleType("bot")
    bot_pkg.__path__ = []

    class _Logger:
        @staticmethod
        def info(msg):
            pass

    bot_pkg.LOGGER = _Logger()

    config_pkg = ModuleType("bot.core")
    config_pkg.__path__ = []
    config_manager = ModuleType("bot.core.config_manager")

    class Config:
        ALLDEBRID_API_KEY = "test-key"

    config_manager.Config = Config

    helper_pkg = ModuleType("bot.helper")
    helper_pkg.__path__ = []
    ext_utils_pkg = ModuleType("bot.helper.ext_utils")
    ext_utils_pkg.__path__ = []
    exceptions_mod = ModuleType("bot.helper.ext_utils.exceptions")

    class DirectDownloadLinkException(Exception):
        pass

    exceptions_mod.DirectDownloadLinkException = DirectDownloadLinkException

    mlu_pkg = ModuleType("bot.helper.mirror_leech_utils")
    mlu_pkg.__path__ = []
    download_utils_pkg = ModuleType(
        "bot.helper.mirror_leech_utils.download_utils"
    )
    download_utils_pkg.__path__ = [
        str(
            project_root
            / "bot"
            / "helper"
            / "mirror_leech_utils"
            / "download_utils"
        )
    ]

    monkeypatch.setitem(sys.modules, "bot", bot_pkg)
    monkeypatch.setitem(sys.modules, "bot.core", config_pkg)
    monkeypatch.setitem(sys.modules, "bot.core.config_manager", config_manager)
    monkeypatch.setitem(sys.modules, "bot.helper", helper_pkg)
    monkeypatch.setitem(sys.modules, "bot.helper.ext_utils", ext_utils_pkg)
    monkeypatch.setitem(
        sys.modules,
        "bot.helper.ext_utils.exceptions",
        exceptions_mod,
    )
    monkeypatch.setitem(
        sys.modules, "bot.helper.mirror_leech_utils", mlu_pkg
    )
    monkeypatch.setitem(
        sys.modules,
        "bot.helper.mirror_leech_utils.download_utils",
        download_utils_pkg,
    )

    sys.modules.pop(
        "bot.helper.mirror_leech_utils.download_utils.alldebrid_resolver",
        None,
    )
    return importlib.import_module(
        "bot.helper.mirror_leech_utils.download_utils.alldebrid_resolver"
    )


@pytest.mark.asyncio
async def test_resolve_returns_unrestricted_url(alldebrid_module, monkeypatch):
    async def fake_call(method, url, *, params=None, data=None):
        assert "unlock" in url
        assert params["link"] == "https://1fichier.com/?abc"
        return {
            "link": "https://cdn.alldebrid.com/abc/file.bin",
            "filename": "file.bin",
            "filesize": 1024,
        }

    monkeypatch.setattr(alldebrid_module, "_call_api", fake_call)
    out = await alldebrid_module.alldebrid_resolve("https://1fichier.com/?abc")
    assert out == "https://cdn.alldebrid.com/abc/file.bin"


@pytest.mark.asyncio
async def test_resolve_returns_streams_dict(alldebrid_module, monkeypatch):
    async def fake_call(method, url, *, params=None, data=None):
        return {
            "filename": "folder",
            "filesize": 0,
            "streams": [
                {
                    "link": "https://cdn/a.mkv",
                    "filename": "a.mkv",
                    "filesize": 100,
                },
                {
                    "link": "https://cdn/b.mkv",
                    "filename": "b.mkv",
                    "filesize": 200,
                },
            ],
        }

    monkeypatch.setattr(alldebrid_module, "_call_api", fake_call)
    out = await alldebrid_module.alldebrid_resolve("https://mega.nz/folder/x")
    assert isinstance(out, dict)
    assert out["title"] == "folder"
    assert len(out["contents"]) == 2
    assert out["total_size"] == 300
    assert out["contents"][0]["url"] == "https://cdn/a.mkv"


@pytest.mark.asyncio
async def test_resolve_no_link_no_streams_raises(alldebrid_module, monkeypatch):
    async def fake_call(method, url, *, params=None, data=None):
        return {"filename": "thing", "filesize": 0}

    monkeypatch.setattr(alldebrid_module, "_call_api", fake_call)
    with pytest.raises(Exception) as exc_info:
        await alldebrid_module.alldebrid_resolve("https://x.example/file")
    assert "did not return a usable download link" in str(exc_info.value)


@pytest.mark.asyncio
async def test_resolve_requires_api_key(alldebrid_module, monkeypatch):
    monkeypatch.setattr(alldebrid_module.Config, "ALLDEBRID_API_KEY", "")
    with pytest.raises(Exception) as exc_info:
        await alldebrid_module.alldebrid_resolve(
            "https://1fichier.com/?abc"
        )
    assert "ALLDEBRID_API_KEY" in str(exc_info.value)


@pytest.mark.asyncio
async def test_check_supported_handles_missing_api_key(
    alldebrid_module, monkeypatch
):
    monkeypatch.setattr(alldebrid_module.Config, "ALLDEBRID_API_KEY", "")
    assert await alldebrid_module.alldebrid_check_supported(
        "https://1fichier.com/?abc"
    ) is False


@pytest.mark.asyncio
async def test_check_supported_matches_active_host(
    alldebrid_module, monkeypatch
):
    async def fake_call(method, url, *, params=None, data=None):
        return {
            "hosts": {
                "1fichier": {
                    "name": "1fichier",
                    "domains": ["1fichier.com"],
                    "status": True,
                },
                "old": {
                    "name": "old",
                    "domains": ["dead.example.com"],
                    "status": False,
                },
            }
        }

    monkeypatch.setattr(alldebrid_module, "_call_api", fake_call)
    assert await alldebrid_module.alldebrid_check_supported(
        "https://1fichier.com/?abc"
    )
    assert await alldebrid_module.alldebrid_check_supported(
        "https://www.1fichier.com/?abc"
    )
    assert not await alldebrid_module.alldebrid_check_supported(
        "https://random-example-xyz.com/x"
    )
    # Inactive host not eligible.
    assert not await alldebrid_module.alldebrid_check_supported(
        "https://dead.example.com/x"
    )
