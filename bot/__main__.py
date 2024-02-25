from aiofiles import open as aiopen
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from os import path as ospath, remove as osremove, execl as osexecl
from sys import executable
from subprocess import run as srun

from bot import bot, LOGGER, OWNER_ID
from .helper.telegram_helper.filters import CustomFilters
from .helper.ext_utils.db_handler import DbManger
from .helper.telegram_helper.button_build import ButtonMaker
from .helper.telegram_helper.message_utils import sendMessage, editMessage
from .modules import contact_with_owner, users, samsung_fw_extractor, site_info_1, site_info_2


@bot.on_message(filters.command("start"))
async def start(client, message):
    if message.chat.type != message.chat.type.PRIVATE:
        return await message.reply_text("This bot is only available for using in private chat")
    userid = message.from_user.id
    buttons = ButtonMaker()
    buttons.ubutton("Channel", "https://t.me/AtrociousMirrorBackup")
    buttons.ubutton("Owner", "https://t.me/ItsBitDefender")
    reply_markup = buttons.build_menu(2)
    start_string = f"Hlw i am assistant bot of <b>Discover Everything</b>."
    await sendMessage(message, start_string, reply_markup)
    await DbManger().update_pm_users(message.from_user.id)


@bot.on_message(filters.command("restart") & CustomFilters.owner)
async def restart(client, message):
    restart_message = await sendMessage(message, "Restarting...")
    srun(["python3", "update.py"])
    await editMessage(restart_message, f"Bot Restarted.")
    osexecl(executable, executable, "-m", "bot")


@bot.on_message(filters.command("stop"))
async def start(client, message):
    await message.reply_text(f"Stoping bot.")
    await exit()


async def restart_notification():
    if await aiopath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
    else:
        chat_id, msg_id = 0, 0

    if await aiopath.isfile(".restartmsg"):
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text='Restarted Successfully!')
        except:
            pass
        await aioremove(".restartmsg")
    else:
        try:
            await bot.send_message(OWNER_ID, "Bot started!")
        except:
            pass

async def main():
    pass


bot.loop.run_forever()
