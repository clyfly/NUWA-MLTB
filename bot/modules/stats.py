from time import time
from re import search as research
from asyncio import gather
from aiofiles.os import path as aiopath
from psutil import (
    disk_usage,
    cpu_percent,
    swap_memory,
    cpu_count,
    virtual_memory,
    net_io_counters,
    boot_time,
)

from .. import bot_start_time, task_dict
from ..helper.ext_utils.status_utils import get_readable_file_size, get_readable_time
from ..helper.ext_utils.bot_utils import cmd_exec, new_task
from ..helper.telegram_helper.message_utils import send_message

commands = {
    "aria2": (["xria", "--version"], r"aria2 version ([\d.]+)"),
    "qBittorrent": (["xnox", "--version"], r"qBittorrent v([\d.]+)"),
    "SABnzbd+": (["xnzb", "--version"], r"sabnzbdplus-([\d.]+)"),
    "python": (["python3", "--version"], r"Python ([\d.]+)"),
    "rclone": (["xone", "--version"], r"rclone v([\d.]+)"),
    "yt-dlp": (["yt-dlp", "--version"], r"([\d.]+)"),
    "ffmpeg": (["xtra", "-version"], r"ffmpeg version ([\d.]+(-\w+)?).*"),
    "7z": (["7z", "i"], r"7-Zip ([\d.]+)"),
}


@new_task
async def bot_stats(_, message):
    total, used, free, disk = disk_usage("/")
    swap = swap_memory()
    memory = virtual_memory()
    per_cpu = cpu_percent(interval=1, percpu=True)
    per_cpu_str = " | ".join([f"CPU{i+1}: {round(p)}%" for i, p in enumerate(per_cpu)])
    stats = f"""
<b>Commit Date:</b> {commands["commit"]}

<b>Bot Uptime:</b> {get_readable_time(time() - bot_start_time)}
<b>OS Uptime:</b> {get_readable_time(time() - boot_time())}

<b>Total Disk Space:</b> {get_readable_file_size(total)}
<b>Used:</b> {get_readable_file_size(used)} | <b>Free:</b> {get_readable_file_size(free)}

<b>Upload:</b> {get_readable_file_size(net_io_counters().bytes_sent)}
<b>Download:</b> {get_readable_file_size(net_io_counters().bytes_recv)}

<b>CPU:</b> {cpu_percent(interval=1)}%
<b>CPU Cores:</b>
{per_cpu_str}

<b>RAM:</b> {memory.percent}%
<b>DISK:</b> {disk}%

<b>Physical Cores:</b> {cpu_count(logical=False)}
<b>Total Cores:</b> {cpu_count()}
<b>SWAP:</b> {get_readable_file_size(swap.total)} | <b>Used:</b> {swap.percent}%

<b>Memory Total:</b> {get_readable_file_size(memory.total)}
<b>Memory Free:</b> {get_readable_file_size(memory.available)}
<b>Memory Used:</b> {get_readable_file_size(memory.used)}

<b>python:</b> {commands["python"]}
<b>aria2:</b> {commands["aria2"]}
<b>qBittorrent:</b> {commands["qBittorrent"]}
<b>SABnzbd+:</b> {commands["SABnzbd+"]}
<b>rclone:</b> {commands["rclone"]}
<b>yt-dlp:</b> {commands["yt-dlp"]}
<b>ffmpeg:</b> {commands["ffmpeg"]}
<b>7z:</b> {commands["7z"]}
"""
    await send_message(message, stats)


@new_task
async def analytics_stats(_, message):
    """Show download/upload analytics for the bot owner."""
    from ..helper.ext_utils.analytics import get_global_stats, get_user_stats
    from ..helper.ext_utils.bot_utils import get_readable_file_size as grfs

    gstats = get_global_stats()
    active_tasks = len(task_dict)

    msg = f"""<b>📊 Bot Analytics</b>

<b>Active Tasks:</b> {active_tasks}
<b>Total Users:</b> {gstats['total_users']}
<b>Total Downloads:</b> {gstats['total_downloads']}
<b>Total Uploads:</b> {gstats['total_uploads']}
<b>Downloaded:</b> {grfs(gstats['total_bytes_downloaded'])}
<b>Uploaded:</b> {grfs(gstats['total_bytes_uploaded'])}
<b>Completed:</b> {gstats['total_completed']}
<b>Failed:</b> {gstats['total_failed']}
"""
    success_rate = 0
    total = gstats['total_completed'] + gstats['total_failed']
    if total > 0:
        success_rate = round((gstats['total_completed'] / total) * 100, 1)
    msg += f"<b>Success Rate:</b> {success_rate}%"

    await send_message(message, msg)


async def get_version_async(command, regex):
    try:
        out, err, code = await cmd_exec(command)
        if code != 0:
            return f"Error: {err}"
        match = research(regex, out)
        return match.group(1) if match else "Version not found"
    except Exception as e:
        return f"Exception: {str(e)}"


@new_task
async def get_packages_version():
    tasks = [get_version_async(command, regex) for command, regex in commands.values()]
    versions = await gather(*tasks)
    for tool, version in zip(commands.keys(), versions):
        commands[tool] = version
    if await aiopath.exists(".git"):
        last_commit = await cmd_exec(
            "git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'", True
        )
        last_commit = last_commit[0]
    else:
        last_commit = "No UPSTREAM_REPO"
    commands["commit"] = last_commit
