"""Ban / Unban user management.

Owner and Sudo users can ban or unban any user from using the bot.
Banned users are stored in ``user_data`` with a ``BANNED`` flag and
persisted to MongoDB via the existing db_handler.
"""

from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

from .. import LOGGER, user_data
from ..core.config_manager import Config
from ..helper.ext_utils.bot_utils import new_task, update_user_ldata
from ..helper.ext_utils.localization import get_string
from ..helper.telegram_helper.bot_commands import BotCommands
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.message_utils import send_message
from ..helper.ext_utils.db_handler import database


def is_user_banned(user_id: int) -> bool:
    """Check if a user is banned."""
    if user_id == Config.OWNER_ID:
        return False
    udata = user_data.get(user_id, {})
    return bool(udata.get("BANNED", False))


def get_ban_reason(user_id: int) -> str:
    """Return the ban reason for a user, or empty string."""
    udata = user_data.get(user_id, {})
    return udata.get("BAN_REASON", "")


@new_task
async def ban_user(_, message):
    """Ban a user: /ban <user_id> [reason]"""
    if len(message.command) < 2:
        await send_message(
            message,
            "<b>Usage:</b> <code>/ban user_id [reason]</code>\n\n"
            "Example: <code>/ban 123456789 Spamming</code>",
        )
        return

    try:
        target_id = int(message.command[1])
    except ValueError:
        await send_message(message, "❌ Invalid user ID.")
        return

    if target_id == Config.OWNER_ID:
        await send_message(message, "❌ Cannot ban the bot owner.")
        return

    reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason specified"

    udata = user_data.get(target_id, {})
    if udata.get("BANNED", False):
        lang = udata.get("USER_LANGUAGE", Config.BOT_LANGUAGE)
        await send_message(
            message,
            get_string("user_already_banned", lang, user_id=target_id),
        )
        return

    update_user_ldata(target_id, "BANNED", True)
    update_user_ldata(target_id, "BAN_REASON", reason)

    if database.db is not None:
        await database.update_user_data(target_id)

    LOGGER.info(f"User {target_id} banned by {message.from_user.id}. Reason: {reason}")
    await send_message(
        message,
        f"✅ User <code>{target_id}</code> has been banned.\n"
        f"Reason: <b>{reason}</b>",
    )


@new_task
async def unban_user(_, message):
    """Unban a user: /unban <user_id>"""
    if len(message.command) < 2:
        await send_message(
            message,
            "<b>Usage:</b> <code>/unban user_id</code>",
        )
        return

    try:
        target_id = int(message.command[1])
    except ValueError:
        await send_message(message, "❌ Invalid user ID.")
        return

    udata = user_data.get(target_id, {})
    if not udata.get("BANNED", False):
        await send_message(
            message,
            f"ℹ️ User <code>{target_id}</code> is not banned.",
        )
        return

    update_user_ldata(target_id, "BANNED", False)
    update_user_ldata(target_id, "BAN_REASON", "")

    if database.db is not None:
        await database.update_user_data(target_id)

    LOGGER.info(f"User {target_id} unbanned by {message.from_user.id}")
    await send_message(
        message,
        f"✅ User <code>{target_id}</code> has been unbanned.",
    )


@new_task
async def list_banned(_, message):
    """List all banned users: /banlist"""
    banned = [
        (uid, d.get("BAN_REASON", ""))
        for uid, d in user_data.items()
        if d.get("BANNED", False)
    ]
    if not banned:
        await send_message(message, "✅ No banned users.")
        return

    msg = "<b>🚫 Banned Users:</b>\n\n"
    for uid, reason in banned:
        msg += f"• <code>{uid}</code> — {reason}\n"

    await send_message(message, msg)