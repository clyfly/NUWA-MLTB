"""Simple per-user rate limiter for bot commands.

Prevents abuse by limiting how many commands a user can send within
a configurable time window. Owner and sudo users are exempt.
"""

from asyncio import Lock
from collections import defaultdict
from time import time

from ... import LOGGER
from ...core.config_manager import Config

# Default: 10 commands per 60 seconds per user
_DEFAULT_RATE = 10
_DEFAULT_WINDOW = 60

_user_timestamps: dict[int, list[float]] = defaultdict(list)
_lock = Lock()


async def is_rate_limited(user_id: int) -> bool:
    """Check whether *user_id* has exceeded the command rate limit.

    Returns ``True`` when the user should be blocked, ``False`` otherwise.
    """
    # Owner is never rate-limited
    if user_id == Config.OWNER_ID:
        return False

    limit = getattr(Config, "RATE_LIMIT_PER_MIN", _DEFAULT_RATE)
    window = getattr(Config, "RATE_LIMIT_WINDOW", _DEFAULT_WINDOW)

    if limit <= 0:
        return False

    now = time()
    async with _lock:
        timestamps = _user_timestamps[user_id]
        # Prune timestamps outside the window
        _user_timestamps[user_id] = [t for t in timestamps if now - t < window]
        if len(_user_timestamps[user_id]) >= limit:
            LOGGER.warning(
                f"Rate limit exceeded for user {user_id} "
                f"({len(_user_timestamps[user_id])} commands in {window}s)"
            )
            return True
        _user_timestamps[user_id].append(now)
        return False


async def get_rate_limit_info(user_id: int) -> tuple[int, int]:
    """Return (current_count, limit) for a user."""
    limit = getattr(Config, "RATE_LIMIT_PER_MIN", _DEFAULT_RATE)
    window = getattr(Config, "RATE_LIMIT_WINDOW", _DEFAULT_WINDOW)
    now = time()
    async with _lock:
        timestamps = _user_timestamps.get(user_id, [])
        current = len([t for t in timestamps if now - t < window])
    return current, limit


async def reset_rate_limit(user_id: int) -> None:
    """Reset the rate limit counter for a user (admin operation)."""
    async with _lock:
        _user_timestamps.pop(user_id, None)