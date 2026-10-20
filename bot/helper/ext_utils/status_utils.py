from html import escape
from psutil import virtual_memory, cpu_percent, disk_usage
from time import time
from asyncio import gather
from inspect import iscoroutinefunction
from pyrogram.types import InputRichMessage

from ... import task_dict, task_dict_lock, bot_start_time, status_dict, DOWNLOAD_DIR
from ...core.config_manager import Config
from ..telegram_helper.button_build import ButtonMaker
from .links_utils import is_gdrive_id, is_rclone_path

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
    STATUS_METADATA = "Metadata"


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
    "MD": MirrorStatus.STATUS_METADATA,
    "PA": MirrorStatus.STATUS_PAUSED,
    "CK": MirrorStatus.STATUS_CHECK,
}


async def get_task_by_gid(gid: str):
    async with task_dict_lock:
        for tk in task_dict.values():
            if hasattr(tk, "seeding"):
                await tk.update()
            if tk.gid() == gid:
                return tk
        return None


async def get_specific_tasks(status, user_id):
    if status == "All":
        if user_id:
            return [tk for tk in task_dict.values() if tk.listener.user_id == user_id]
        else:
            return list(task_dict.values())
    tasks_to_check = (
        [tk for tk in task_dict.values() if tk.listener.user_id == user_id]
        if user_id
        else list(task_dict.values())
    )
    coro_tasks = []
    coro_tasks.extend(tk for tk in tasks_to_check if iscoroutinefunction(tk.status))
    coro_statuses = await gather(*[tk.status() for tk in coro_tasks])
    result = []
    coro_index = 0
    for tk in tasks_to_check:
        if tk in coro_tasks:
            st = coro_statuses[coro_index]
            coro_index += 1
        else:
            st = tk.status()
        if (st == status) or (
            status == MirrorStatus.STATUS_DOWNLOAD and st not in STATUSES.values()
        ):
            result.append(tk)
    return result


async def get_all_tasks(req_status: str, user_id):
    async with task_dict_lock:
        return await get_specific_tasks(req_status, user_id)


def get_readable_file_size(size_in_bytes):
    if not size_in_bytes:
        return "0B"

    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1

    return f"{size_in_bytes:.2f}{SIZE_UNITS[index]}"


def get_readable_time(seconds: int):
    periods = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    result = ""
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f"{int(period_value)}{period_name}"
    return result or "0s"


def time_to_seconds(time_duration):
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
    except (ValueError, AttributeError, IndexError):
        return 0


def speed_string_to_bytes(size_text: str):
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


def get_progress_bar_string(pct):
    try:
        pct = float(pct.strip("%"))
    except:
        pct = 0
    p = min(max(pct, 0), 100)
    cFull = min(12, max(0, int(p / 8.333333333333334)))
    p_str = "■" * cFull + "□" * (12 - cFull)
    return f"[{p_str}]"


def _get_elapsed_time(task):
    try:
        listener = getattr(task, "listener", None)
        if hasattr(task, "start_time") and task.start_time > 0:
            elapsed = time() - task.start_time
        elif listener and hasattr(listener, "message") and getattr(listener.message, "date", None):
            elapsed = time() - listener.message.date.timestamp()
        else:
            elapsed = 0
        res = get_readable_time(int(max(0, elapsed)))
        return res or "0s"
    except:
        return "0s"


def _get_upload_dest(task):
    try:
        listener = getattr(task, "listener", None)
        if not listener:
            return "Telegram"
        if getattr(listener, "is_leech", False):
            return "Telegram"
        if getattr(listener, "is_gofile", False):
            return "GoFile"
        if getattr(listener, "is_buzzheavier", False):
            return "BuzzHeavier"
        if getattr(listener, "is_clone", False):
            return "GDrive Clone"
        up_dest = getattr(listener, "up_dest", "")
        if up_dest:
            if is_gdrive_id(up_dest):
                return "Google Drive"
            elif is_rclone_path(up_dest):
                return "Rclone"
            return str(up_dest)
        return "Telegram"
    except:
        return "Telegram"


def _get_engine_name(task):
    try:
        tool = getattr(task, "tool", "")
        try:
            from ...modules.stats import commands
        except:
            commands = {}

        if tool == "qbittorrent":
            ver = commands.get("qBittorrent")
            if isinstance(ver, str) and ver and not ver.startswith(("Error", "Exception", "Version")):
                return f"qBit v{ver}"
            return "qBit"
        elif tool == "aria2":
            ver = commands.get("aria2")
            if isinstance(ver, str) and ver and not ver.startswith(("Error", "Exception", "Version")):
                return f"Aria2 v{ver}"
            return "Aria2"
        elif tool == "yt-dlp":
            ver = commands.get("yt-dlp")
            if isinstance(ver, str) and ver and not ver.startswith(("Error", "Exception", "Version")):
                return f"yt-dlp v{ver}"
            return "yt-dlp"
        elif tool == "sabnzbd":
            ver = commands.get("SABnzbd+")
            if isinstance(ver, str) and ver and not ver.startswith(("Error", "Exception", "Version")):
                return f"Sabnzbd v{ver}"
            return "Sabnzbd"
        elif tool == "rclone":
            ver = commands.get("rclone")
            if isinstance(ver, str) and ver and not ver.startswith(("Error", "Exception", "Version")):
                return f"Rclone v{ver}"
            return "Rclone"
        elif tool == "ffmpeg":
            ver = commands.get("ffmpeg")
            if isinstance(ver, str) and ver and not ver.startswith(("Error", "Exception", "Version")):
                return f"FFmpeg v{ver}"
            return "FFmpeg"
        elif tool == "7z":
            ver = commands.get("7z")
            if isinstance(ver, str) and ver and not ver.startswith(("Error", "Exception", "Version")):
                return f"7z v{ver}"
            return "7z"
        elif tool == "telegram":
            return "Telegram"
        elif tool == "jdownloader":
            return "JDownloader"
        elif tool == "gofile":
            return "GoFile"
        elif tool == "buzzheavier":
            return "BuzzHeavier"
        elif tool == "gDriveApi":
            return "Google Drive"
        elif tool:
            return tool.capitalize()
        return "Unknown"
    except:
        return "Unknown"


def _get_user_display(task):
    try:
        listener = getattr(task, "listener", None)
        if not listener:
            return "User"
        user = getattr(listener, "user", None)
        user_id = getattr(listener, "user_id", 0)
        name = ""
        if user:
            name = getattr(user, "first_name", None) or getattr(user, "title", None) or ""
        if not name:
            name = str(user_id) if user_id else "User"
        escaped_name = escape(str(name))
        if user_id:
            return f"<a href='tg://user?id={user_id}'>{escaped_name}</a> ({user_id})"
        return escaped_name
    except:
        return "User"


async def get_readable_message(sid, is_user, page_no=1, status="All", page_step=1):
    tasks = await get_specific_tasks(status, sid if is_user else None)

    tasks_no = len(tasks)
    if tasks_no == 0:
        if status == "All":
            return None, None
        else:
            return InputRichMessage(html=f"No Active {status} Tasks!<br><br>"), None

    STATUS_LIMIT = Config.STATUS_LIMIT or 10
    pages = (max(tasks_no, 1) + STATUS_LIMIT - 1) // STATUS_LIMIT
    if page_no > pages:
        page_no = (page_no - 1) % pages + 1
        status_dict[sid]["page_no"] = page_no
    elif page_no < 1:
        page_no = pages - (abs(page_no) % pages)
        status_dict[sid]["page_no"] = page_no
    start_position = (page_no - 1) * STATUS_LIMIT

    if pages > 1:
        msg = f"<h3>Tasks: {tasks_no} | Page: {page_no}/{pages}</h3>"
    else:
        msg = f"<h3>Tasks: {tasks_no}</h3>"

    for index, task in enumerate(
        tasks[start_position : STATUS_LIMIT + start_position], start=1
    ):
        if status != "All":
            tstatus = status
        elif iscoroutinefunction(task.status):
            tstatus = await task.status()
        else:
            tstatus = task.status()
        
        link = (
            task.listener.message.link
            if getattr(task.listener, "is_super_chat", False)
            and getattr(task.listener.message, "link", None)
            else ""
        )
        msg += "<hr>"
        if link:
            msg += f"<b>{index + start_position}. <a href='{link}'>{tstatus}</a></b>"
        else:
            msg += f"<b>{index + start_position}. {tstatus}</b>"

        if task.listener.subname:
            msg += f"<br><i>{escape(task.listener.subname)}</i>"

        if (
            tstatus not in [MirrorStatus.STATUS_SEED, MirrorStatus.STATUS_QUEUEUP]
            and task.listener.progress
        ):
            progress = task.progress()
            msg += f"<br>{get_progress_bar_string(progress)} » {progress}"
            if task.listener.subname:
                subsize = f"/{get_readable_file_size(task.listener.subsize)}"
                ac = len(task.listener.files_to_proceed)
                count = f"{task.listener.proceed_count}/{ac or '?'}"
            else:
                subsize = ""
                count = ""
            msg += f"<br><b>Processed:</b> {task.processed_bytes()}{subsize}"
            if count:
                msg += f"<br><b>Count:</b> {count}"
            msg += f"<br><b>Size:</b> {task.size()}"
            msg += f"<br><b>Speed:</b> {task.speed()}"
            msg += f"<br><b>ETA:</b> {task.eta()}"
            if (
                tstatus == MirrorStatus.STATUS_DOWNLOAD
                and (getattr(task.listener, "is_torrent", False) or getattr(task.listener, "is_qbit", False))
            ):
                try:
                    s_num = task.seeders_num()
                    l_num = task.leechers_num()
                    if s_num is not None and l_num is not None:
                        msg += f"<br><b>Seeders:</b> {s_num} | <b>Leechers:</b> {l_num}"
                except:
                    pass
            msg += f"<br><b>Elapsed:</b> {_get_elapsed_time(task)}"
            msg += f"<br><b>Upload:</b> {_get_upload_dest(task)}"
            msg += f"<br><b>Engine:</b> {_get_engine_name(task)}"
            msg += f"<br><b>User:</b> {_get_user_display(task)}"
        elif tstatus == MirrorStatus.STATUS_SEED:
            msg += f"<br><b>Size:</b> {task.size()}"
            msg += f"<br><b>Speed:</b> {task.seed_speed()}"
            msg += f"<br><b>Uploaded:</b> {task.uploaded_bytes()}"
            msg += f"<br><b>Ratio:</b> {task.ratio()}"
            msg += f" | <b>Time:</b> {task.seeding_time()}"
            msg += f"<br><b>Elapsed:</b> {_get_elapsed_time(task)}"
            msg += f"<br><b>Engine:</b> {_get_engine_name(task)}"
            msg += f"<br><b>User:</b> {_get_user_display(task)}"
        else:
            msg += f"<br><b>Size:</b> {task.size()}"
            msg += f"<br><b>Elapsed:</b> {_get_elapsed_time(task)}"
            msg += f"<br><b>Upload:</b> {_get_upload_dest(task)}"
            msg += f"<br><b>Engine:</b> {_get_engine_name(task)}"
            msg += f"<br><b>User:</b> {_get_user_display(task)}"

        msg += f"<br><tg-button type='callback_data' data='cancel canconf {task.gid()}' style='danger'>Cancel Task</tg-button>"
        if (
            (getattr(task, "tool", "") == "aria2" and getattr(task.listener, "is_torrent", False))
            or getattr(task, "tool", "") in ["qbittorrent", "sabnzbd"]
        ) and tstatus in [
            MirrorStatus.STATUS_DOWNLOAD,
            MirrorStatus.STATUS_PAUSED,
            MirrorStatus.STATUS_QUEUEDL,
        ]:
            msg += f" | <tg-button type='callback_data' data='sel select {task.gid()}' style='primary'>Select Files</tg-button>"
        if tstatus != MirrorStatus.STATUS_UPLOAD and (
            Config.QUEUE_ALL or Config.QUEUE_DOWNLOAD or Config.QUEUE_UPLOAD
        ):
            if tstatus == MirrorStatus.STATUS_QUEUEDL:
                msg += f" | <tg-button type='callback_data' data='force run {task.gid()}' style='success'>ForceRun</tg-button>"
                msg += f" | <tg-button type='callback_data' data='force fd {task.gid()}' style='success'>ForceDl</tg-button>"
                if not task.listener.force_upload:
                    msg += f" | <tg-button type='callback_data' data='force fu {task.gid()}' style='success'>ForceUp</tg-button>"
            elif not task.listener.force_upload and (
                tstatus == MirrorStatus.STATUS_DOWNLOAD or not task.listener.force_run
            ):
                msg += f" | <tg-button type='callback_data' data='force fu {task.gid()}' style='success'>ForceUp</tg-button>"
        msg += "<br><br>"

    buttons = ButtonMaker()
    if not is_user:
        buttons.data_button("📜", f"status {sid} ov", position="header")
    if len(tasks) > STATUS_LIMIT:
        buttons.data_button("<<", f"status {sid} pre", position="header")
        buttons.data_button(">>", f"status {sid} nex", position="header")
        if tasks_no > 30:
            for i in [1, 2, 4, 6, 8, 10, 15]:
                buttons.data_button(i, f"status {sid} ps {i}", position="footer")
    if status != "All" or tasks_no > 20:
        for label, status_value in list(STATUSES.items()):
            if status_value != status:
                buttons.data_button(label, f"status {sid} st {status_value}")
    buttons.data_button("♻️", f"status {sid} ref", position="header", style="green")
    button = buttons.build_menu(8)
    msg += f"<b>CPU:</b> {cpu_percent()}% | <b>FREE:</b> {get_readable_file_size(disk_usage(DOWNLOAD_DIR).free)}"
    msg += f"<br><b>RAM:</b> {virtual_memory().percent}% | <b>UPTIME:</b> {get_readable_time(time() - bot_start_time)}"
    return InputRichMessage(html=msg), button
