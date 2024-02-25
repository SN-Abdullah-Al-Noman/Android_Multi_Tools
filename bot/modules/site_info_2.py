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

    replied_msg = message.reply_to_message
    site_code, site_info = replied_msg.text.split()
    await message.reply(f"{note_name} {main_note}")

    conn = MongoClient(DATABASE_URL)
    db = conn.mltb
    collection = db.gp_site_info
    collection.update_one(
                {'site_code': site_code},
                {'$set': {'site_info': site_info}},
                upsert=True)
        
