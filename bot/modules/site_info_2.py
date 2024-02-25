from pyrogram.filters import command
from pyrogram.handlers import MessageHandler
from pymongo import MongoClient

from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters


DATABASE_URL = "mongodb+srv://Atrocious-Robot:Cjka8UGjoN1Nj9gB@atrocious-robot.2quemf3.mongodb.net/?retryWrites=true&w=majority"


@bot.on_message(command("save"))
async def save_note(client, message):
    if not DATABASE_URL:
        return await message.reply("No database added.")

    client = MongoClient(DATABASE_URL)
    db = client.grameenphone
    collection = client.grameenphone_site_info
    note_name = message.text.split(maxsplit=1)
    if len(note_name) < 2:
        await message.reply("Please provide a note name.")
        return
    site_code = note_name[1].strip()

    if message.reply_to_message:
        site_info = message.reply_to_message.text
        collection.insert_one({"site_code": site_code, "site_info": site_info})
        await message.reply(f"{site_code} info saved in database")
    else:
        await message.reply("Please reply to a message to save it as a note.")