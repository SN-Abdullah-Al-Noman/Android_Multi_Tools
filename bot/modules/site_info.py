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
            encoded_image = b64encode(image_file.read()).decode('utf-8')
            collection.update_one({'site_code': site_code}, {'$set': {'site_info': site_info, 'site_photo': encoded_image}}, upsert=True)
    elif message.reply_to_message.text:
        site_info = message.reply_to_message.text
        collection.update_one({'site_code': site_code}, {'$set': {'site_info': site_info}}, upsert=True)
    else:
        return await message.reply("Please reply anything with command to save it.\n\n<b>Usage:</b> /save note_name")

    await message.reply(f"<b>{site_code}</b> site information added in database.")


@bot.on_message(command("info"))
async def get_note(client, message):
    if not DATABASE_URL:
        return await message.reply("No database added.")

    args = message.text.split()
    if len(args) > 1:
        site_code = args[1]
    else:
        return await message.reply("Please provide site code after command.\n\n<b>Usage:</b> /info site_code")

    conn = MongoClient(DATABASE_URL)
    db = conn.mltb
    collection = db.gp_site_info
    site_info = collection.find_one({'site_code': site_code})

    if site_info:
        response = f"<b>Site Code:</b> {site_info['site_code']}\n"
        response += f"<b>Site Info:</b> {site_info.get('site_info', 'N/A')}\n"
        if 'site_photo' in site_info:
            decoded_data = b64decode(site_info['site_photo'])
            with open(f"{site_code}.jpg", 'wb') as image:
                image.write(decoded_data)
            with open(f"{site_code}.jpg", 'rb') as image:
                await message.reply_photo(image, caption=response)
        else:
            await message.reply(response)
    else:
        await message.reply(f"<b>{site_code}</b> Site's information not found. Because it's not added yet.")


@bot.on_message(command("sites"))
async def list_sites(client, message):
    if not DATABASE_URL:
        return await message.reply("No database added.")

    conn = MongoClient(DATABASE_URL)
    db = conn.mltb
    collection = db.gp_site_info
    site_codes = collection.distinct("site_code")

    if site_codes:
        response = "<b>SL:</b>  <b>Site Code:</b>\n"
        for idx, site_code in enumerate(site_codes, start=1):
            response += f"<b>{idx:02}:</b>  <code>{site_code}</code>\n"
        await message.reply(response)
    else:
        await message.reply("No site's info added in database.")
