from os import path as ospath, remove as osremove, execl as osexecl
from sys import executable
from subprocess import run as srun

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


async def restart(client, message):
    msg = message.text
    if msg.startswith("restart"):
        restart_message = await sendMessage(message, "Restarting...")
        srun(["python3", "update.py"])
        await editMessage(restart_message, f"Bot Restarted.")
        osexecl(executable, executable, "-m", "bot")
        


@bot.on_message()
async def check_sites(client, message):
    await restart(client, message)
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
