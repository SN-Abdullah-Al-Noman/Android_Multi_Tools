from pyrogram import filters
from pyrogram.handlers import MessageHandler

from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters


async def editMessage(message, text):
    try:
        await message.edit(text=text)
    except Exception as e:
        print(f"An error occurred: {e}")


AG_SITES = """
BGCOS1
BGDBL1
BGDBH1
"""

BGCOS1 = f" <b>A</b> Class. <b>170</b> Links."

@bot.on_message()
async def check_sites(client, message):
    non_ag_sites = []
    if not message.text.startswith("HS MF KHE:") or message.text.startswith("HS BATT KHE:") or message.text.startswith("HS DOWN KHE:") or message.text.startswith("HS GCELL KHE:") or message.text.startswith("HS UCELL KHE:"): 
        return

    if message.text.startswith("HS MF KHE:") or message.text.startswith("HS BATT KHE:") or message.text.startswith("HS DOWN KHE:") or message.text.startswith("HS GCELL KHE:") or message.text.startswith("HS UCELL KHE:"):
        msg = message.text.split('\n')
        sites = '\n'.join(msg[1:])

    ag_sites_list = []
    for site in sites.strip().split('\n'):
        site_code = site.split('(')[0].strip()
        if site_code in AG_SITES.strip().split('\n'):
            if site_code == "BGCOS1":
                site += BGCOS1
            elif site_code == "BGDBL1":
                site += " Additional info for BGDBL1"
            ag_sites_list.append(site)
        else:
            non_ag_sites.append(site)

    if ag_sites_list:
        ag_sites_str = '\n'.join(ag_sites_list)
        await message.reply(f"<b>AG Sites:\nSites:      Time:</b>\n{ag_sites_str}")

    non_ag_sites_str = '\n'.join(non_ag_sites)
    if non_ag_sites_str:
        await message.reply(f"<b>Non Generator Sites:\nSites:      Time:</b>\n{non_ag_sites_str}")
