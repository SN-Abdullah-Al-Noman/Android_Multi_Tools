import requests
import base64
import json

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.filters import command
from pyrogram.handlers import MessageHandler
from pyrogram.errors import UserNotParticipant

from bot import bot, FSUB_IDS
from bot.helper.telegram_helper.filters import CustomFilters

username = "apiauth"
password = "Xw2_5j_BDdlT"
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
url = "https://www3.69dot.me/3x/"
headers = {'Authorization': f'Basic {credentials}', 'Accept': 'application/json',}


async def get_number_info(num):
    params = {'num': num}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        html_start = response.text.find('<style>')
        if html_start != -1:
            json_part = response.text[:html_start]
        else:
            json_part = response.text

        try:
            data = json.loads(json_part.strip())
            info = data['info']
            result = "<b>Here is the number info :</b>\n\n"
            result += f"<b>• Name:</b> <code>{info['Name']}</code>\n"
            result += f"<b>• Number:</b> <code>{info['Number']}</code>\n"
            result += f"<b>• N-ID:</b> <code>{info['nid']}</code>\n"
            result += f"<b>• Date Of Birth:</b> <code>{info['DOB']}</code>\n"
            result += f"<b>• Company:</b> <code>{info['Sim']}</code>\n"
            result += f"<b>• Sim-Type:</b> <code>{info['Sim-Type']}</code>\n"
            return result
        except Exception as e:
            return f'An error occurred when trying to parse the response to JSON: {e}'
    else:
        return f'Request failed with status code {response.status_code}'


async def chat_info(FSUB_IDS):
    if FSUB_IDS.startswith('-100'):
        FSUB_IDS = int(FSUB_IDS)
    elif FSUB_IDS.startswith('@'):
        FSUB_IDS = FSUB_IDS.replace('@', '')
    else:
        return None
    try:
        chat = await bot.get_chat(FSUB_IDS)
        return chat
    except PeerIdInvalid as e:
        LOGGER.error(f"{e.NAME}: {e.MESSAGE} for {FSUB_IDS}")
        return None


async def force_subscribe(message):
    if FSUB_IDS:
        chat = await chat_info(FSUB_IDS)
        try:
            await chat.get_member(message.from_user.id)
        except UserNotParticipant:
            if username := chat.username:
                invite_link = f"https://t.me/{username}"
            else:
                invite_link = chat.invite_link
            button_text = f"Join {chat.title}"
            button_url = f"{invite_link}"
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=button_url)]])
            return await message.reply(f"You must be a member of the channel to use this bot.", reply_markup=reply_markup)
        

async def send_number_info(client, message):
    if await force_subscribe(message):
        return
    if len(message.text.split(' ')) < 2:
        return await message.reply("<b>Please provide a Robi SIM number after the command.</b>\n\n<b>Example:</b>\n/crack তোমার গার্লফ্রেন্ডের নম্বর")

    num = message.text.split(' ')[1]
    response = await get_number_info(num)
    await message.reply(response)

bot.add_handler(MessageHandler(send_number_info, filters=command("crack") & CustomFilters.sim_info_checker_chats))
