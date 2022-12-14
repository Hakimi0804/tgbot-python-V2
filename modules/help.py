"""
Module to send message with help strings when requested.
Available methods:

    bot_help(update, context):
        Sends help message.
"""
import logging
from util.help import Help
from telegram import Update
from telegram.ext import ContextTypes
log = logging.getLogger("help-module")


async def bot_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(Help.get_help())

Help.register_help("help", "Show help message.")
