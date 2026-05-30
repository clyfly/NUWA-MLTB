"""Tests for the AllDebrid magnet/torrent flow."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture
def alldebrid_module(monkeypatch):
    project_root = Path(__file__).resolve().parent.parent

    bot_pkg = ModuleType("bot")
    bot_pkg.__path__ = []

    class _Logger:
        @staticmethod
        def info(msg):
            pass

        @staticmethod
        def warning(msg):
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
        sys.modules, "bot.helper.ext_utils.exceptions", exceptions_mod
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


def test_extract_infohash(alldebrid_module):
    info = alldebrid_module._extract_infohash(
        "magnet:?xt=urn:btih:0123456789abcdef0123456789abcdef01234567&dn=foo"
    )
    assert info == "0123456789abcdef0123456789abcdef01234567"


def test_canonicalize_magnet(alldebrid_module):
    canonical = alldebrid_module._canonicalize_magnet(
        "magnet:?xt=urn:btih:ABC123&tr=udp://x&dn=Some+Name"
    )
    assert canonical.startswith("magnet:?xt=urn:btih:abc123")
    assert "tr=" not in canonical
    assert "dn=Some" in canonical


def test_flatten_files_recursive(alldebrid_module):
    nodes = [
        {
            "n": "Folder",
            "e": [
                {"n": "a.mkv", "s": 100, "l": "https://alldebrid.com/f/A"},
                {
                    "n": "Inner",
                    "e": [
                        {"n": "b.mkv", "s": 200, "l": "https://alldebrid.com/f/B"},
                    ],
                },
            ],
        },
        {"n": "c.mkv", "s": 300, "l": "https://alldebrid.com/f/C"},
    ]
    out = alldebrid_module._flatten_files(nodes)
    paths = [item["path"] for item in out]
    assert paths == ["Folder/a.mkv", "Folder/Inner/b.mkv", "c.mkv"]
    sizes = [item["size"] for item in out]
    assert sizes == [100, 200, 300]


@pytest.mark.asyncio
async def test_resolve_magnet_full_flow(alldebrid_module, monkeypatch):
    state = {"poll_calls": 0}

    async def fake_upload_magnet(magnet):
        return {"id": 999, "name": "movie.x264", "size": 600}

    async def fake_get_status(magnet_id):
        state["poll_calls"] += 1
        # First call: still downloading. Second call: ready.
        if state["poll_calls"] == 1:
            return {"statusCode": 1, "status": "Downloading", "seeders": 5}
        return {"statusCode": 4, "status": "Ready", "seeders": 5}

    async def fake_get_files(magnet_id):
        return [
            {"filename": "a.mkv", "path": "a.mkv", "size": 100, "link": "/f/A"},
            {"filename": "b.mkv", "path": "b.mkv", "size": 200, "link": "/f/B"},
        ]

    async def fake_unlock(link):
        return {"link": f"https://cdn{link}", "filename": "auto", "filesize": 0}

    async def fake_delete(magnet_id):
        return True

    monkeypatch.setattr(alldebrid_module, "upload_magnet", fake_upload_magnet)
    monkeypatch.setattr(alldebrid_module, "get_magnet_status", fake_get_status)
    monkeypatch.setattr(alldebrid_module, "get_magnet_files", fake_get_files)
    monkeypatch.setattr(
        alldebrid_module, "_unlock_alldebrid_link", fake_unlock
    )
    monkeypatch.setattr(alldebrid_module, "delete_magnet", fake_delete)

    progress_seen: list[dict] = []

    async def progress(snapshot):
        progress_seen.append(snapshot)

    out = await alldebrid_module.alldebrid_resolve_magnet(
        "magnet:?xt=urn:btih:abc",
        progress_callback=progress,
        poll_interval=0,  # zero sleep for test speed
    )
    assert out["magnet_id"] == 999
    assert out["title"] == "movie.x264"
    assert out["total_size"] == 300
    assert len(out["contents"]) == 2
    assert out["contents"][0]["url"].startswith("https://cdn")
    # Progress callback fires for both poll and unlock phases.
    phases = {snap.get("phase") for snap in progress_seen}
    assert "torrent" in phases
    # Unlock progress events have unlock_done/unlock_total instead.
    assert any("unlock_done" in snap for snap in progress_seen)


@pytest.mark.asyncio
async def test_resolve_magnet_error_status_deletes_magnet(
    alldebrid_module, monkeypatch
):
    deleted: list[int] = []

    async def fake_upload_magnet(magnet):
        return {"id": 7, "name": "x", "size": 1}

    async def fake_get_status(magnet_id):
        return {"statusCode": 15, "status": "No peers", "seeders": 0}

    async def fake_delete(magnet_id):
        deleted.append(magnet_id)
        return True

    monkeypatch.setattr(alldebrid_module, "upload_magnet", fake_upload_magnet)
    monkeypatch.setattr(alldebrid_module, "get_magnet_status", fake_get_status)
    monkeypatch.setattr(alldebrid_module, "delete_magnet", fake_delete)

    with pytest.raises(Exception) as exc_info:
        await alldebrid_module.alldebrid_resolve_magnet(
            "magnet:?xt=urn:btih:abc",
            poll_interval=0,
        )
    assert "AllDebrid" in str(exc_info.value)
    # Cleanup ran even though the upload happened.
    assert deleted == [7]


@pytest.mark.asyncio
async def test_resolve_magnet_respects_cancellation(
    alldebrid_module, monkeypatch
):
    deleted: list[int] = []
    cancelled = {"value": False}

    async def fake_upload_magnet(magnet):
        return {"id": 11, "name": "x", "size": 1}

    async def fake_get_status(magnet_id):
        # Trigger cancellation on the first poll.
        cancelled["value"] = True
        return {"statusCode": 1, "status": "Downloading", "seeders": 0}

    async def fake_delete(magnet_id):
        deleted.append(magnet_id)
        return True

    monkeypatch.setattr(alldebrid_module, "upload_magnet", fake_upload_magnet)
    monkeypatch.setattr(alldebrid_module, "get_magnet_status", fake_get_status)
    monkeypatch.setattr(alldebrid_module, "delete_magnet", fake_delete)

    def is_cancelled():
        return cancelled["value"]

    with pytest.raises(Exception) as exc_info:
        await alldebrid_module.alldebrid_resolve_magnet(
            "magnet:?xt=urn:btih:abc",
            is_cancelled=is_cancelled,
            poll_interval=0,
        )
    # First check (before status) lets the loop into the body, status
    # call flips the flag, the next iteration short-circuits with the
    # cancellation message.
    assert "cancelled" in str(exc_info.value).lower()
    assert deleted == [11]


@pytest.mark.asyncio
async def test_resolve_magnet_empty_files_raises(alldebrid_module, monkeypatch):
    deleted: list[int] = []

    async def fake_upload_magnet(magnet):
        return {"id": 33, "name": "x", "size": 0}

    async def fake_get_status(magnet_id):
        return {"statusCode": 4, "status": "Ready", "seeders": 5}

    async def fake_get_files(magnet_id):
        return []

    async def fake_delete(magnet_id):
        deleted.append(magnet_id)
        return True

    monkeypatch.setattr(alldebrid_module, "upload_magnet", fake_upload_magnet)
    monkeypatch.setattr(alldebrid_module, "get_magnet_status", fake_get_status)
    monkeypatch.setattr(alldebrid_module, "get_magnet_files", fake_get_files)
    monkeypatch.setattr(alldebrid_module, "delete_magnet", fake_delete)

    with pytest.raises(Exception) as exc_info:
        await alldebrid_module.alldebrid_resolve_magnet(
            "magnet:?xt=urn:btih:abc",
            poll_interval=0,
        )
    assert "no files" in str(exc_info.value).lower()
    assert deleted == [33]
