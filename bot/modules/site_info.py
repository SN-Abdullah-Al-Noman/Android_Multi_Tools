from base64 import b64encode, b64decode
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

    args = message.text.split()
    if len(args) > 1:
        site_code = args[1]
    else:
        return await message.reply("Please reply anything with command to save it.\n\n<b>Usage:</b> /save note_name")

    conn = MongoClient(DATABASE_URL)
    db = conn.mltb
    collection = db.gp_site_info

    if message.reply_to_message.photo:
    site_info = message.reply_to_message.caption
    site_photo = f"site_photos/{site_code}.jpg"
    await message.reply_to_message.download(site_photo)
    with open(site_photo, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        collection.update_one({'site_code': site_code}, {'$set': {'site_info': site_info, 'site_photo': encoded_image}}, upsert=True)
    elif message.reply_to_message.text:
        site_info = message.reply_to_message.text
        collection.update_one({'site_code': site_code}, {'$set': {'site_info': site_info}}, upsert=True)
    else:
        return await message.reply("Please reply anything with command to save it.\n\n<b>Usage:</b> /save note_name")

    await message.reply(f"<b>{site_code}</b> site information added in database.")
