# SPDX-License-Identifier: GPL-3.0-only
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Copyright (c) 2024, Firdaus Hakimi <hakimifirdaus944@gmail.com>

import os
import time
import logging

import telegram.error

from util import module
from util.help import Help

from telegram import Chat, ChatMember, ChatMemberAdministrator, ChatMemberLeft, Update, Bot
from telegram.ext import Application, ContextTypes, CommandHandler, CallbackQueryHandler

TOKEN_OK = True
log: logging.Logger = logging.getLogger(__name__)


class ModuleMetadata(module.ModuleMetadata):
    @classmethod
    def setup_module(cls, app: Application):
        app.add_handler(CommandHandler("fastpurge", fastpurge, block=False))
        app.add_handler(CommandHandler("anonfastpurge", anonfastpurge, block=False))


try:
    from api_token import TOKEN
except ImportError:
    if not (TOKEN := os.getenv("BOT_TOKEN")):
        log.error("Cannot get bot token.")
        TOKEN_OK = False


async def anonfastpurge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verify admin
    admins: list[ChatMemberAdministrator] = await update.effective_chat.get_administrators()  # type: ignore
    if update.callback_query.from_user.id not in [admin.user.id for admin in admins]:
        await update.callback_query.answer("You're not admin smh")
        return

    # Start purging!
    message = await update.callback_query.edit_message_text("Purging...")
    # Extract startpurge and endpurge from callback_data
    callback_data = update.callback_query.data
    start_id = int(callback_data.split(":")[1].split("=")[1])
    end_id = int(callback_data.split(":")[2].split("=")[1])

    time_taken = await _purge(update.effective_chat.id,
                              start_id,
                              end_id,
                              update.get_bot())

    await update.callback_query.edit_message_text(f"Purged {end_id - start_id} messages in {time_taken:.3f}s")


async def anonfastpurge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # To check anoniminity, we use get_chat_member and check if it returns ChatMemberLeft
    member = await update.effective_chat.get_member(update.effective_user.id)
    if type(member) != ChatMemberLeft:
        await update.message.reply_text("You're not even anonymous, use /fastpurge instead")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message smh")
        return

    callback_data = "{}:startpurge={}:endpurge={}".format(__name__,
                                                          update.message.reply_to_message.id,
                                                          update.message.id)

    markup: list[list[telegram.InlineKeyboardButton]] = [[
        telegram.InlineKeyboardButton("Yes", callback_data=callback_data)
    ]]

    await update.message.reply_text("Press this button to confirm you're an admin",
                                    reply_markup=telegram.InlineKeyboardMarkup(markup))

    context.application.add_handler(CallbackQueryHandler(anonfastpurge_handler,
                                                         pattern=callback_data,
                                                         block=False))


async def fastpurge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert TOKEN_OK
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message smh")
        return

    message = await update.message.reply_text("Checking admin status")
    admins: tuple[ChatMemberAdministrator] = await update.effective_chat.get_administrators()  # type: ignore
    log.info(f"Chat admins: {admins}")
    if not any(update.effective_user.id == admin.user.id for admin in admins):
        await message.edit_text("You're not admin smh\n"
                                "If you are anonymous admin, please use /anonfastpurge\n"
                                "Technically it can be combined into this command, but this was meant to "
                                "avoid spamming telegram server, to prevent the bot from getting timed out.")
        return
    if not any(update.get_bot().id == admin.user.id for admin in admins):
        await message.edit_text("I'm not admin smh")
        return

    await message.edit_text(f"Purging {update.message.id - update.message.reply_to_message.id} messages")

    time_taken = await _purge(update.effective_chat.id,
                              update.message.reply_to_message.id,
                              update.message.id,
                              update.get_bot())
    await message.edit_text(f"Purged {update.message.id - update.message.reply_to_message.id} in {time_taken:.3f}")


async def _purge(chat_id: int, start_message_id: int, end_message_id: int, bot: Bot) -> float:
    """
    Purge messages from a chat.

    This function deletes messages in a chat from a given start message ID to a stop message ID. 
    It returns the time taken to complete the purge.

    Args:
        chat_id (int): The ID of the chat where messages are to be deleted.
        start_message_id (int): The starting message ID for the purge. Usually update.message.reply_to_message.id
        end_message_id (int): The stopping message ID for the purge. Usually update.message.id
        bot (Bot): The bot instance used to delete the messages.

    Returns:
        float: The time taken to complete the purge in seconds.
    """
    purge_start_time = time.time()

    message_list: list[int] = [msgid for msgid in range(start_message_id, end_message_id + 1)]
    while len(message_list) > 0:
        if len(message_list) > 100:
            await bot.delete_messages(chat_id, message_list[:100])  # type: ignore
            message_list = message_list[100:]
        else:
            await bot.delete_messages(chat_id, message_list)  # type: ignore
            message_list.clear()

    purge_end_time = time.time()
    return purge_end_time - purge_start_time


Help.register_help("fastpurge", "Purge message with insane speed")
Help.register_help("anonfastpurge", "Purge message with insane speed, but only for anonymous admins")
