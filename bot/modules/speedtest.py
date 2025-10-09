from speedtest import Speedtest

from bot import LOGGER
from bot.core.nuwa_client import TgClient
from bot.helper.ext_utils.bot_utils import new_task
from bot.helper.ext_utils.status_utils import get_readable_file_size
from bot.helper.telegram_helper.message_utils import (
    delete_message,
    edit_message,
    send_message,
)


@new_task
async def speedtest(_, message):
    status_message = await send_message(message, "⚡ Initializing Speedtest, please wait...")

    def run_speedtest():
        test = Speedtest()
        test.get_best_server()
        test.download()
        test.upload()
        return test.results

    result = await TgClient.bot.loop.run_in_executor(None, run_speedtest)

    if not result:
        await edit_message(status_message, "⚠️ Speedtest could not complete. Please try again later.")
        return

    output = (
        "<b>SPEEDTEST RESULTS</b>\n\n"
        f"• <b>Ping:</b> <code>{result.ping} ms</code>\n"
        f"• <b>Upload Speed:</b> <code>{get_readable_file_size(result.upload / 8)}/s</code>\n"
        f"• <b>Download Speed:</b> <code>{get_readable_file_size(result.download / 8)}/s</code>\n"
        f"• <b>IP Address:</b> <code>{result.client['ip']}</code>"
    )

    try:
        await send_message(message, output)
        await delete_message(status_message)
    except Exception as e:
        LOGGER.error(str(e))
        await edit_message(status_message, output)