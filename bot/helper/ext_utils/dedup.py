"""File deduplication — prevents downloading the same file twice.

Tracks recently completed downloads by (name, size) or by URL.
When a new download is requested the module checks the cache and
returns a match if one exists, so the bot can skip or warn.
"""

from asyncio import Lock
from hashlib import sha256
from time import time

from ... import LOGGER
from ...core.config_manager import Config

# {dedup_key: {"path": str, "timestamp": float, "user_id": int}}
_cache: dict[str, dict] = {}
_lock = Lock()

# Key: how long (seconds) to remember a downloaded file
_TTL = 3600 * 6  # 6 hours default


def _make_key(name: str = "", size: int = 0, url: str = "") -> str:
    """Build a deterministic cache key."""
    if url:
        return f"url:{sha256(url.encode()).hexdigest()}"
    if name and size:
        return f"ns:{sha256(f'{name}:{size}'.encode()).hexdigest()}"
    return ""


async def check_duplicate(
    name: str = "",
    size: int = 0,
    url: str = "",
    user_id: int = 0,
) -> dict | None:
    """Return cached info if the file was already downloaded recently.

    Returns ``None`` when there is no match (safe to proceed).
    Returns a dict ``{"path": ..., "timestamp": ..., "user_id": ...}``
    when a duplicate is detected.
    """
    if not getattr(Config, "DEDUP_ENABLED", False):
        return None

    key = _make_key(name, size, url)
    if not key:
        return None

    async with _lock:
        entry = _cache.get(key)
        if entry is not None:
            age = time() - entry["timestamp"]
            if age < _TTL:
                LOGGER.info(
                    f"Dedup hit for '{name}' (age {int(age)}s, "
                    f"user {entry['user_id']})"
                )
                return entry
            else:
                # Expired
                del _cache[key]
    return None


async def register_download(
    name: str = "",
    size: int = 0,
    url: str = "",
    user_id: int = 0,
    path: str = "",
) -> None:
    """Record a successfully completed download in the dedup cache."""
    if not getattr(Config, "DEDUP_ENABLED", False):
        return

    key = _make_key(name, size, url)
    if not key:
        return

    async with _lock:
        _cache[key] = {
            "path": path,
            "timestamp": time(),
            "user_id": user_id,
        }
        LOGGER.info(f"Dedup registered: '{name}' (key={key[:16]}…)")

    # Evict expired entries periodically
    await _evict_expired()


async def _evict_expired() -> None:
    """Remove expired entries from the cache."""
    now = time()
    async with _lock:
        expired = [k for k, v in _cache.items() if now - v["timestamp"] > _TTL]
        for k in expired:
            del _cache[k]


async def clear_cache() -> int:
    """Clear the entire dedup cache. Returns number of entries removed."""
    async with _lock:
        count = len(_cache)
        _cache.clear()
    return count


async def get_cache_stats() -> dict:
    """Return cache statistics."""
    async with _lock:
        total = len(_cache)
        now = time()
        active = sum(1 for v in _cache.values() if now - v["timestamp"] < _TTL)
    return {
        "total_entries": total,
        "active_entries": active,
        "expired_entries": total - active,
        "ttl_seconds": _TTL,
    }