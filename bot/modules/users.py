from sys import executable
from pymongo import MongoClient
from subprocess import run as srun
from base64 import b64encode, b64decode
from os import path as ospath, remove as osremove, execl as osexecl

from pyrogram import filters
from pyrogram.handlers import MessageHandler

from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage


AG_SITES = """
BGCOS1
BGDBL1
BGDBH1
"""

DATABASE_URL = "mongodb+srv://Atrocious-Robot:Cjka8UGjoN1Nj9gB@atrocious-robot.2quemf3.mongodb.net/?retryWrites=true&w=majority"

async def restart(client, message):
    if message.text.startswith("restart"):
        restart_message = await sendMessage(message, "Restarting...")
        srun(["python3", "update.py"])
        await editMessage(restart_message, f"Bot Restarted.")
        osexecl(executable, executable, "-m", "bot")
        

async def check_sites(client, message):
    ag_sites_list = []
    non_ag_sites = []
    msg = message.text
    msg = msg.split('\n')
    sites = '\n'.join(msg[1:])

    for site in sites.strip().split('\n'):
        site_code = site.split('(')[0].strip()
        if site_code in AG_SITES.strip().split('\n'):
            if site_code == "BGCOS1":
                site += f"  <b>A</b> Class. <b>170</b> Links."
            elif site_code == "BGDBL1":
                site += " Additional info for BGDBL1"
            ag_sites_list.append(site)
        else:
            non_ag_sites.append(site)

    if ag_sites_list:
        ag_sites_str = '\n'.join(ag_sites_list)
        await message.reply(f"<b>Auto Generator Sites:\nSites:      Time:    Types:    Links:</b>\n{ag_sites_str}")

    non_ag_sites_str = '\n'.join(non_ag_sites)
    if non_ag_sites_str:
        await message.reply(f"<b>Non Generator Sites:\nSites:      Time:    Types:    Links:</b>\n{non_ag_sites_str}")



async def save_site_info(client, message):
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



async def get_site_info(client, message):
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


async def site_list(client, message):
    if message.text.startswith("sites"):
        if not DATABASE_URL:
            return await message.reply("No database added.")
        else:
            pass

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


async def delete_site_info(client, message):
    if not DATABASE_URL:
        return await message.reply("No database added.")

    args = message.text.split()
    if len(args) > 1:
        site_code = args[1]
    else:
        return await message.reply("Please provide site code after command.\n\n<b>Usage:</b> /delete site_code")

    conn = MongoClient(DATABASE_URL)
    db = conn.mltb
    collection = db.gp_site_info

    if collection.find_one({'site_code': site_code}):
        collection.delete_one({'site_code': site_code})
        await message.reply(f"Site information for <b>{site_code}</b> has been successfully deleted.")
    else:
        await message.reply(f"No information found for site code <b>{site_code}</b>.")


@bot.on_message()
async def check_command(client, message):
    await restart(client, message)
    await site_list(client, message)
