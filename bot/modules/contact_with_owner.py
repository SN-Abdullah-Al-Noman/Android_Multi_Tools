from pyrogram import Client, filters
from pyrogram.types import User
from pytz import timezone
from datetime import datetime

from bot import bot, OWNER_ID

@bot.on_message(filters.private & filters.command("send"))
async def forward_to_owner(client, message):
    msg = message.text.split()
    if len(msg) > 1:
        main_message = msg[1]
    else:
        main_message = ""
    if not main_message:
        return await message.reply(f"Please write something after command")
    user_id = message.from_user.id
    user = await client.get_users(user_id)
    dhaka_timezone = timezone('Asia/Dhaka')
    dhaka_time = message.date.astimezone(dhaka_timezone)
    formatted_time = dhaka_time.strftime('%d %B %Y %I:%M %p')
    
    info = f"<b>Name:</b> {user.first_name}\n"
    info += f"<b>Username:</b>  @{user.username}\n"
    info += f"<b>User ID:</b> <code>{user.id}</code>\n"
    info += f"<b>Is Bot:</b> {user.is_bot}\n"
    info += f"<b>Time:</b> {formatted_time}\n\n"
    info += f"<b>Main Message:</b>\n{main_message}"
    
    await bot.send_message(OWNER_ID, info)
