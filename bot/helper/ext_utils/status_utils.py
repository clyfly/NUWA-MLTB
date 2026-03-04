from html import escape
from psutil import virtual_memory, cpu_percent, disk_usage
from time import time
from asyncio import iscoroutinefunction, gather
from typing import Optional, List, Any, Dict
import logging
from enum import Enum

from ... import task_dict, task_dict_lock, bot_start_time, status_dict, DOWNLOAD_DIR
from ...core.config_manager import Config
from ..telegram_helper.button_build import ButtonMaker
from ..telegram_helper.bot_commands import BotCommands

# Setup logging
logger = logging.getLogger(__name__)

SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]


class MirrorStatus:
    STATUS_UPLOAD = "Upload"
    STATUS_DOWNLOAD = "Download"
    STATUS_CLONE = "Clone"
    STATUS_QUEUEDL = "QueueDl"
    STATUS_QUEUEUP = "QueueUp"
    STATUS_PAUSED = "Pause"
    STATUS_ARCHIVE = "Archive"
    STATUS_EXTRACT = "Extract"
    STATUS_SPLIT = "Split"
    STATUS_CHECK = "CheckUp"
    STATUS_SEED = "Seed"
    STATUS_SAMVID = "SamVid"
    STATUS_CONVERT = "Convert"
    STATUS_FFMPEG = "FFmpeg"


STATUSES = {
    "ALL": "All",
    "DL": MirrorStatus.STATUS_DOWNLOAD,
    "UP": MirrorStatus.STATUS_UPLOAD,
    "QD": MirrorStatus.STATUS_QUEUEDL,
    "QU": MirrorStatus.STATUS_QUEUEUP,
    "AR": MirrorStatus.STATUS_ARCHIVE,
    "EX": MirrorStatus.STATUS_EXTRACT,
    "SD": MirrorStatus.STATUS_SEED,
    "CL": MirrorStatus.STATUS_CLONE,
    "CM": MirrorStatus.STATUS_CONVERT,
    "SP": MirrorStatus.STATUS_SPLIT,
    "SV": MirrorStatus.STATUS_SAMVID,
    "FF": MirrorStatus.STATUS_FFMPEG,
    "PA": MirrorStatus.STATUS_PAUSED,
    "CK": MirrorStatus.STATUS_CHECK,
}


class StatusConfig:
    """Configuration constants for status display."""
    PROGRESS_BAR_BLOCKS = 12
    BUTTONS_PER_ROW = 8
    LARGE_TASK_THRESHOLD = 30
    PAGE_STEP_OPTIONS = [1, 2, 4, 6, 8, 10, 15]
    STATUS_FILTER_THRESHOLD = 20
    MAX_NAME_LENGTH = 50
    TELEGRAM_MAX_MESSAGE = 4000  # Reserve some space for buttons


async def get_task_by_gid(gid: str):
    """
    Retrieve a task by its GID.
    
    Args:
        gid: Global ID of the task
        
    Returns:
        Task object if found, None otherwise
    """
    async with task_dict_lock:
        for tk in task_dict.values():
            if hasattr(tk, "seeding"):
                await tk.update()
            if tk.gid() == gid:
                return tk
        return None


async def get_specific_tasks(status: str, user_id: Optional[int] = None) -> List[Any]:
    """
    Get tasks filtered by status and user.
    
    Args:
        status: Status filter ('All' or specific status)
        user_id: User ID to filter by, None for all users
        
    Returns:
        List of tasks matching the criteria
    """
    if status == "All":
        if user_id:
            return [tk for tk in task_dict.values() if tk.listener.user_id == user_id]
        return list(task_dict.values())
    
    tasks_to_check = (
        [tk for tk in task_dict.values() if tk.listener.user_id == user_id]
        if user_id
        else list(task_dict.values())
    )
    
    # Separate coroutine and non-coroutine status methods
    coro_tasks = [tk for tk in tasks_to_check if iscoroutinefunction(tk.status)]
    sync_tasks = [tk for tk in tasks_to_check if not iscoroutinefunction(tk.status)]
    
    # Gather coroutine statuses concurrently
    coro_statuses = await gather(*[tk.status() for tk in coro_tasks]) if coro_tasks else []
    
    result = []
    
    # Add coroutine tasks with their statuses
    for tk, st in zip(coro_tasks, coro_statuses):
        if (st == status) or (
            status == MirrorStatus.STATUS_DOWNLOAD and st not in STATUSES.values()
        ):
            result.append(tk)
    
    # Add sync tasks
    for tk in sync_tasks:
        st = tk.status()
        if (st == status) or (
            status == MirrorStatus.STATUS_DOWNLOAD and st not in STATUSES.values()
        ):
            result.append(tk)
    
    return result


async def get_all_tasks(req_status: str, user_id: Optional[int] = None) -> List[Any]:
    """
    Thread-safe wrapper for get_specific_tasks.
    
    Args:
        req_status: Status filter
        user_id: User ID to filter by
        
    Returns:
        List of tasks matching the criteria
    """
    async with task_dict_lock:
        return await get_specific_tasks(req_status, user_id)


def get_readable_file_size(size_in_bytes: float) -> str:
    """
    Convert bytes to human readable format.
    
    Args:
        size_in_bytes: Size in bytes
        
    Returns:
        Formatted string like "1.23GB"
    """
    if not size_in_bytes:
        return "0B"

    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1

    return f"{size_in_bytes:.2f}{SIZE_UNITS[index]}"


def get_readable_time(seconds: int) -> str:
    """
    Convert seconds to human readable time.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string like "1d2h3m4s"
    """
    if seconds < 0:
        return "0s"
    
    periods = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    result = ""
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f"{int(period_value)}{period_name}"
    return result or "0s"


def time_to_seconds(time_duration: str) -> float:
    """
    Convert time string (HH:MM:SS or MM:SS) to seconds.
    
    Args:
        time_duration: Time string to parse
        
    Returns:
        Total seconds
    """
    try:
        parts = time_duration.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = map(float, parts)
        elif len(parts) == 2:
            hours = 0
            minutes, seconds = map(float, parts)
        elif len(parts) == 1:
            hours = 0
            minutes = 0
            seconds = float(parts[0])
        else:
            return 0
        return hours * 3600 + minutes * 60 + seconds
    except (ValueError, AttributeError):
        return 0


def speed_string_to_bytes(size_text: str) -> float:
    """
    Convert speed string (like "1MB/s") to bytes.
    
    Args:
        size_text: Speed string to parse
        
    Returns:
        Speed in bytes
    """
    try:
        size = 0
        size_text = size_text.lower()
        if "k" in size_text:
            size += float(size_text.split("k")[0]) * 1024
        elif "m" in size_text:
            size += float(size_text.split("m")[0]) * 1048576
        elif "g" in size_text:
            size += float(size_text.split("g")[0]) * 1073741824
        elif "t" in size_text:
            size += float(size_text.split("t")[0]) * 1099511627776
        elif "b" in size_text:
            size += float(size_text.split("b")[0])
        return size
    except (ValueError, AttributeError):
        return 0


def get_progress_bar_string(pct_str: str) -> str:
    """
    Generate a visual progress bar.
    
    Args:
        pct_str: Percentage string like "45%"
        
    Returns:
        Progress bar string like "[■■■■□□□□□□]"
    """
    try:
        pct = float(pct_str.strip('%'))
        p = min(max(pct, 0), 100)
        filled = int(p * StatusConfig.PROGRESS_BAR_BLOCKS // 100)
        return "■" * filled + "□" * (StatusConfig.PROGRESS_BAR_BLOCKS - filled)
    except (ValueError, AttributeError):
        return "□" * StatusConfig.PROGRESS_BAR_BLOCKS


def truncate_name(name: str, max_length: int = StatusConfig.MAX_NAME_LENGTH) -> str:
    """
    Truncate long names with ellipsis.
    
    Args:
        name: Original name
        max_length: Maximum allowed length
        
    Returns:
        Truncated name if needed
    """
    if len(name) <= max_length:
        return name
    return name[:max_length-3] + "..."


def format_task_details(task, tstatus: str, index: int) -> str:
    """
    Format a single task's details into HTML string.
    
    Args:
        task: Task object
        tstatus: Current status of the task
        index: Task number for display
        
    Returns:
        Formatted HTML string for the task
    """
    parts = []
    
    # Header with status and name
    if task.listener.is_super_chat:
        parts.append(f"<b>{index}.<a href='{task.listener.message.link}'>{tstatus}</a>: </b>")
    else:
        parts.append(f"<b>{index}.{tstatus}: </b>")
    
    # Task name (truncated if needed)
    name = truncate_name(str(task.name()))
    parts.append(f"<code>{escape(name)}</code>")
    
    # Subname if exists
    if task.listener.subname:
        parts.append(f"\n<i>{escape(str(task.listener.subname))}</i>")
    
    parts.append("<blockquote>")
    
    # Progress details for active tasks
    if tstatus not in [MirrorStatus.STATUS_SEED, MirrorStatus.STATUS_QUEUEUP] and task.listener.progress:
        progress = task.progress()
        parts.append(f"\n{get_progress_bar_string(progress)} {progress}")
        
        # Processed bytes with optional subsize
        processed = task.processed_bytes()
        if task.listener.subname:
            subsize = f"/{get_readable_file_size(task.listener.subsize)}"
            ac = len(task.listener.files_to_proceed)
            count = f"{task.listener.proceed_count}/{ac or '?'}"
        else:
            subsize = ""
            count = ""
        
        parts.append(f"\n• <b>Processed:</b> {processed}{subsize}")
        if count:
            parts.append(f"\n• <b>Count:</b> {count}")
        parts.append(f"\n• <b>Size:</b> {task.size()}")
        parts.append(f"\n• <b>Speed:</b> {task.speed()}")
        parts.append(f"\n• <b>ETA:</b> {task.eta()}")
        
        # Torrent-specific info
        if tstatus == MirrorStatus.STATUS_DOWNLOAD and (task.listener.is_torrent or task.listener.is_qbit):
            try:
                seeders = task.seeders_num()
                leechers = task.leechers_num()
                parts.append(f"\n• <b>Seeders:</b> {seeders} | <b>Leechers:</b> {leechers}")
            except AttributeError:
                pass  # Method not implemented
            except Exception as e:
                logger.debug(f"Error getting seeders/leechers: {e}")
    
    # Seeding details
    elif tstatus == MirrorStatus.STATUS_SEED:
        parts.append(f"\n• <b>Size: </b>{task.size()}")
        parts.append(f"\n• <b>Speed: </b>{task.seed_speed()}")
        parts.append(f"\n• <b>Uploaded: </b>{task.uploaded_bytes()}")
        parts.append(f"\n• <b>Ratio: </b>{task.ratio()}")
        parts.append(f" | <b>Time: </b>{task.seeding_time()}")
    
    # Other statuses (just size)
    else:
        parts.append(f"\n• <b>Size: </b>{task.size()}")
    
    # GID and close blockquote
    parts.append(f"\n• <b>Gid: </b><code>{task.gid()}</code>")
    parts.append("</blockquote>")
    parts.append(f"<code>/cancel {task.gid()}</code>\n\n")
    
    return "".join(parts)


async def get_readable_message(sid: str, is_user: bool, page_no: int = 1, 
                              status: str = "All", page_step: int = 1):
    """
    Generate readable status message with buttons.
    
    Args:
        sid: Session ID
        is_user: Whether this is a user request
        page_no: Current page number
        status: Status filter
        page_step: Number of tasks per page step
        
    Returns:
        Tuple of (message_text, button_markup)
    """
    msg_parts = []
    button = None

    # Get filtered tasks
    tasks = await get_specific_tasks(status, sid if is_user else None)

    STATUS_LIMIT = Config.STATUS_LIMIT
    tasks_no = len(tasks)
    pages = (max(tasks_no, 1) + STATUS_LIMIT - 1) // STATUS_LIMIT
    
    # Adjust page number if out of bounds
    if page_no > pages:
        page_no = (page_no - 1) % pages + 1
        status_dict[sid]["page_no"] = page_no
    elif page_no < 1:
        page_no = pages - (abs(page_no) % pages)
        status_dict[sid]["page_no"] = page_no
    
    start_position = (page_no - 1) * STATUS_LIMIT
    end_position = STATUS_LIMIT + start_position
    current_tasks = tasks[start_position:end_position]

    # Format each task
    for index, task in enumerate(current_tasks, start=1):
        # Get task status
        if status != "All":
            tstatus = status
        elif iscoroutinefunction(task.status):
            tstatus = await task.status()
        else:
            tstatus = task.status()
        
        # Format task details
        task_msg = format_task_details(task, tstatus, index + start_position)
        msg_parts.append(task_msg)
        
        # Check message length limit
        if len("".join(msg_parts)) > StatusConfig.TELEGRAM_MAX_MESSAGE:
            msg_parts = msg_parts[:-1]  # Remove last task
            msg_parts.append("\n⚠️ <i>Too many tasks, showing partial list</i>\n")
            break

    msg = "".join(msg_parts)

    # Handle empty results
    if not msg:
        if status == "All":
            return None, None
        msg = f"No Active {status} Tasks!\n\n"

    # Build buttons
    buttons = ButtonMaker()
    
    if not is_user:
        buttons.data_button("ᴛᴀsᴋ", f"status {sid} ov", position="header")
    
    # Pagination buttons
    if len(tasks) > STATUS_LIMIT:
        msg += f"<b>Page:</b> {page_no}/{pages} | <b>Tasks:</b> {tasks_no} | <b>Step:</b> {page_step}\n"
        buttons.data_button("<<", f"status {sid} pre", position="header")
        buttons.data_button(">>", f"status {sid} nex", position="header")
        
        if tasks_no > StatusConfig.LARGE_TASK_THRESHOLD:
            for step in StatusConfig.PAGE_STEP_OPTIONS:
                buttons.data_button(str(step), f"status {sid} ps {step}", position="footer")
    
    # Status filter buttons
    if status != "All" or tasks_no > StatusConfig.STATUS_FILTER_THRESHOLD:
        for label, status_value in STATUSES.items():
            if status_value != status:
                buttons.data_button(label, f"status {sid} st {status_value}")
    
    # Refresh button
    buttons.data_button("♻️", f"status {sid} ref", position="header")
    
    button = buttons.build_menu(StatusConfig.BUTTONS_PER_ROW)
    
    # System stats footer
    msg += f"<b>CPU:</b> {cpu_percent()}% | <b>FREE:</b> {get_readable_file_size(disk_usage(DOWNLOAD_DIR).free)}"
    msg += f"\n<b>RAM:</b> {virtual_memory().percent}% | <b>UPTIME:</b> {get_readable_time(time() - bot_start_time)}"
    
    return msg, button