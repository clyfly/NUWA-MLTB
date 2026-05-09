from speedtest import Speedtest
from datetime import datetime, timezone
from bot import LOGGER
from bot.core.telegram_manager import TgClient
from bot.helper.ext_utils.bot_utils import new_task
from bot.helper.ext_utils.status_utils import get_readable_file_size
from bot.helper.telegram_helper.message_utils import (
    delete_message,
    edit_message,
    send_message,
)

@new_task
async def speedtest(_, message):
    status_message = await send_message(message, "⏳ <b>Running speed test...</b>\n<i>This may take a moment.</i>")

    def run_speedtest():
        test = Speedtest()
        test.get_best_server()
        test.download()
        test.upload()
        return test.results

    result = await TgClient.bot.loop.run_in_executor(None, run_speedtest)

    if not result:
        await edit_message(status_message, "❌ <b>Speedtest failed.</b> Please try again later.")
        return

    # Format timestamp
    raw_time = getattr(result, "timestamp", None)
    try:
        test_time = datetime.fromisoformat(raw_time).astimezone(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    except Exception:
        test_time = raw_time or "N/A"

    # Mask IP: tampilkan hanya oktet pertama
    raw_ip = result.client.get("ip", "N/A")
    try:
        parts = raw_ip.split(".")
        masked_ip = f"{parts[0]}.{parts[1]}.*.*"
    except Exception:
        masked_ip = "N/A"

    download = get_readable_file_size(result.download / 8)
    upload = get_readable_file_size(result.upload / 8)
    ping = result.ping
    server_name = result.server.get("name", "N/A")
    server_country = result.server.get("country", "N/A")
    isp = result.client.get("isp", "N/A")

    output = (
        "📡 <b>Network Speedtest Report</b>\n\n"
        f"🏓 <b>Ping</b>      : <code>{ping:.2f} ms</code>\n"
        f"⬇️ <b>Download</b>  : <code>{download}/s</code>\n"
        f"⬆️ <b>Upload</b>    : <code>{upload}/s</code>\n\n"
        f"🌐 <b>Server</b>    : <code>{server_name}, {server_country}</code>\n"
        f"🏢 <b>ISP</b>       : <code>{isp}</code>\n"
        f"🔒 <b>IP</b>        : <code>{masked_ip}</code>\n"
        f"🕐 <b>Time</b>      : <code>{test_time}</code>\n\n"
        "<i>Powered by CLYFLY Speedtest Service</i>"
    )

    try:
        await send_message(message, output)
        await delete_message(status_message)
    except Exception as e:
        LOGGER.error(f"Speedtest message send failed: {e}")
        await edit_message(status_message, output)