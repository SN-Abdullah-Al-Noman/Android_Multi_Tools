from pyrogram import filters
from pyrogram.handlers import MessageHandler

from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters


async def editMessage(message, text):
    try:
        await message.edit(text=text)
    except Exception as e:
        print(f"An error occurred: {e}")



ag_sites = """
BGCOS1
BGDBL1
BGDBH1
"""

async def check_sites(client, message):
    non_ag_sites = []
    if message.reply_to_message:
        msg = message.reply_to_message.text.split('\n')
        sites = '\n'.join(msg[1:])
        for site in sites.strip().split('\n'):
            if not sites:
                return await message.reply(f"Please reply to any xsite alarm")

    ag_sites_list = []
    for site in sites.strip().split('\n'):
        site_code = site.split('(')[0].strip()
        if site_code in ag_sites.strip().split('\n'):
            ag_sites_list.append(site)
        else:
            non_ag_sites.append(site)

    if ag_sites_list:
        ag_sites_str = '\n'.join(ag_sites_list)
        await message.reply(f"<b>Auto Generator Sites:\nSites:      Time:</b>\n{ag_sites_str}")

    non_ag_sites_str = '\n'.join(non_ag_sites)
    if non_ag_sites_str:
        await message.reply(f"<b>Non Generator Sites:\nSites:      Time:</b>\n{non_ag_sites_str}")

        
bot.add_handler(MessageHandler(check_sites, filters=filters.command("s")))
