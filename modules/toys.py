"""
Modules with useless commands, just for fun.
Available methods:

    random_percentage(update, context)
        returns random gayness/sexiness percentage.

    shuffle(update, context)
        shuffle a sentence.
"""

import logging
import random
import re
import util.module
from util.help import Help
from util.config import Config
from telegram import Update, Message
from telegram.ext import ContextTypes, CommandHandler, Application

log: logging.Logger = logging.getLogger(__name__)
config: Config = Config("toys.json")


class ModuleMetadata(util.module.ModuleMetadata):
    @classmethod
    def setup_module(cls, app: Application):
        app.add_handler(CommandHandler("gay", random_percentage))
        app.add_handler(CommandHandler("sexy", random_percentage))
        app.add_handler(CommandHandler("shuffle", shuffle))
        app.add_handler(CommandHandler("insert", insert))
        app.add_handler(CommandHandler("add_words", add_words))
        app.add_handler(CommandHandler("remove_words", remove_words))
        app.add_handler(CommandHandler("reset_words", reset_words))


async def random_percentage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.reply_to_message is not None:
        user: str = update.message.reply_to_message.from_user.first_name
        user_id: int = update.message.reply_to_message.from_user.id
    else:
        user: str = update.message.from_user.first_name
        user_id: int = update.message.from_user.id

    # Check type, whether sexy or gay
    if re.match(r"^/gay", update.message.text):
        type_: str = "gay"
    else:
        type_: str = "sexy"
    ret: Message = await update.message.reply_text(f"Calculating {type_}ness...")

    if type_ == "gay":
        rand_percent: int = random.randint(0, 10) if user_id == 1024853832 else random.randint(80, 150)
    elif type_ == "sexy":
        rand_percent: int = random.randint(80, 150) if user_id == 1024853832 else random.randint(-50, 50)

    await ret.edit_text(f"{user} is {rand_percent}% {type_}")


async def shuffle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.reply_to_message is None:
        await update.message.reply_text("You must reply to a message.")
        return

    ret: Message = await update.message.reply_text("Shuffling...")
    text: list[str] = update.message.reply_to_message.text.split(" ")
    random.shuffle(text)

    await ret.edit_text(" ".join(text))


Help.register_help("gay", "Return gayness level of you/replied user.")
Help.register_help("sexy", "Return sexiness level of you/replied user.")
Help.register_help("shuffle", "Shuffle replied message.")


def init_insert_words() -> None:
    default_words: str = "bsdk chutiya bc arch fedora dnf pacman gay lesbian pranaya sharan nero bot cum coom bhai bro " \
                         "pro max dick big based rui rui2 rui1 samarbot brainfuck inactive dead optimized lines amazing " \
                         "updated changelog bugs lag adb shell ffs f2fs ext4 ipv6 komaru cute adorable boot rom recovery " \
                         "docker micro rose miss sir exam pactice allow invite python poothon poopthon nodejs js hello " \
                         "world development kit lint fuck fucking madarchod behenchod message maybe ping oof available " \
                         "solution test goes order biggest problem though command root magisk superuser insta facebook " \
                         "fuckbook twitter ot inr 69 vanilla gapps creampie admin link embed why removed knowing certain " \
                         "funny bootloader boobloader unlocked uncocked kang kanger sagar java gawd god samar hakimi " \
                         "mcdonald covid kick ban fart poop pee penis enlarge chup chutiye kek speaking always never los " \
                         "aex realme oplus vooc dart rebrand rust with vast erofs guilty wrong yeet prath joemomma"
    config.config["insert_words"]: list[str] = default_words.split(" ")
    config.write_config()


async def insert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.reply_to_message is None:
        await update.message.reply_text("You must reply to a message.")
        return

    insert_words: list[str] = config.config.get("insert_words")
    input_words: list[str] = update.message.reply_to_message.text.split(" ")
    random_words: list[str] = random.choices(insert_words,
                                             k=len(input_words) if len(input_words) <= len(insert_words) else len(insert_words))  # noqa: E501

    reply_words: list[str] = random_words + input_words
    random.shuffle(reply_words)
    await update.message.reply_text(" ".join(reply_words))


async def add_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config.read_config()
    input_words: list[str] = context.args

    if len(input_words) == 0:
        await update.message.reply_text("You must provide at least one word.")
        return

    reply: Message = await update.message.reply_text("Updating word database")
    info: str = ""
    warnings: str = ""

    insert_words: list[str] = config.config.get("insert_words")
    for word in input_words:
        if word not in insert_words:
            insert_words.append(word)
            info += f"word '{word}' added to database.\n"
        else:
            warnings += f"warning: word '{word}' already exists in database.\n"

    config.config["insert_words"] = insert_words
    config.write_config()

    await reply.edit_text(f"{info}{warnings}\nSuccessfully updated the database.")


async def remove_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config.read_config()
    input_words: list[str] = context.args

    if len(input_words) == 0:
        await update.message.reply_text("You must provide at least one word.")
        return

    reply: Message = await update.message.reply_text("Updating word database")
    info: str = ""
    warnings: str = ""

    insert_words: list[str] = config.config.get("insert_words")
    for word in input_words:
        if word in insert_words:
            insert_words.remove(word)
            info += f"removed word '{word}' from database.\n"
        else:
            warnings += f"warning: word '{word}' does not exist in database.\n"

    config.config["insert_words"]: list[str] = insert_words
    config.write_config()

    await reply.edit_text(f"{info}{warnings}\nSuccessfully updated the database.")


async def reset_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    init_insert_words()
    await update.message.reply_text(f"Word list reset successfully.")


# Make sure insert_words is initialized, otherwise we could cause traceback in insert()
if config.config.get("insert_words") is None:
    init_insert_words()

Help.register_help("insert", "Returns a randomly generated sentence.")
Help.register_help("add_words", "Adds the given words to database for /insert.")
Help.register_help("remove_words", "Removes the given words from database for /insert.")
Help.register_help("reset_words", "Resets the words in database for /insert.")
