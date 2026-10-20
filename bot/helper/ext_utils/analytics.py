"""Lightweight download analytics and statistics tracker.

Tracks per-user download counts, total bytes transferred, and task
completion history. Data is stored in memory (optionally backed by
MongoDB via the existing db_handler).
"""

from collections import defaultdict
from time import time

from ... import LOGGER

# In-memory stats (reset on restart unless loaded from DB)
_user_stats: dict[int, dict] = defaultdict(lambda: {
    "total_downloads": 0,
    "total_uploads": 0,
    "total_bytes_downloaded": 0,
    "total_bytes_uploaded": 0,
    "failed_tasks": 0,
    "completed_tasks": 0,
    "last_active": 0,
})


def record_download(user_id: int, size_bytes: int = 0) -> None:
    """Record a completed download for a user."""
    stats = _user_stats[user_id]
    stats["total_downloads"] += 1
    stats["total_bytes_downloaded"] += size_bytes
    stats["completed_tasks"] += 1
    stats["last_active"] = time()


def record_upload(user_id: int, size_bytes: int = 0) -> None:
    """Record a completed upload for a user."""
    stats = _user_stats[user_id]
    stats["total_uploads"] += 1
    stats["total_bytes_uploaded"] += size_bytes
    stats["completed_tasks"] += 1
    stats["last_active"] = time()


def record_failure(user_id: int) -> None:
    """Record a failed task for a user."""
    stats = _user_stats[user_id]
    stats["failed_tasks"] += 1
    stats["last_active"] = time()


def get_user_stats(user_id: int) -> dict:
    """Get stats for a specific user."""
    return dict(_user_stats.get(user_id, {
        "total_downloads": 0,
        "total_uploads": 0,
        "total_bytes_downloaded": 0,
        "total_bytes_uploaded": 0,
        "failed_tasks": 0,
        "completed_tasks": 0,
        "last_active": 0,
    }))


def get_global_stats() -> dict:
    """Get aggregate stats across all users."""
    totals = {
        "total_users": len(_user_stats),
        "total_downloads": 0,
        "total_uploads": 0,
        "total_bytes_downloaded": 0,
        "total_bytes_uploaded": 0,
        "total_failed": 0,
        "total_completed": 0,
    }
    for stats in _user_stats.values():
        totals["total_downloads"] += stats["total_downloads"]
        totals["total_uploads"] += stats["total_uploads"]
        totals["total_bytes_downloaded"] += stats["total_bytes_downloaded"]
        totals["total_bytes_uploaded"] += stats["total_bytes_uploaded"]
        totals["total_failed"] += stats["failed_tasks"]
        totals["total_completed"] += stats["completed_tasks"]
    return totals