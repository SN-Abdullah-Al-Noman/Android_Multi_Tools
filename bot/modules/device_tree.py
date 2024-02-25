from os import path as ospath, rename as osrename, remove as osremove, getcwd
from pyrogram import filters
from telegraph import upload_file
from asyncio import sleep as asleep
from pyrogram.filters import command
from aiofiles.os import remove as aioremove
from pyrogram.handlers import MessageHandler
from twrpdtgen.device_tree import DeviceTree
from pathlib import Path
from threading import Thread
from subprocess import run as srun

from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters


async def device_tree(client, message):
    if message.reply_to_message and message.reply_to_message.document:
        file_name = message.reply_to_message.document.file_name
        if file_name == "boot.img" or file_name == "recovery.img":
            image_path_str = await message.reply_to_message.download()
            image_path = Path(image_path_str)
            if not image_path.is_file():
                return await message.reply_text("File does not exist.")
            await message.reply_text(f"{file_name} downloaded.")
            output_path = Path("./output")
            device_tree = DeviceTree(image_path)
            device_tree.dump_to_folder(output_path)
            await message.reply_text(f"Device tree generated.")
            srun(["7z", "a", "device_tree.zip", "./output"])
            await bot.send_document(chat_id=message.chat.id, document="device_tree.zip")
            await message.reply_text("Here is your device tree.")
            osremove('image_path')
            osremove('device_tree.zip')
            srun(["rm", "-rf", "output"])
            

bot.add_handler(MessageHandler(device_tree, filters=command("dt") & CustomFilters.owner))
