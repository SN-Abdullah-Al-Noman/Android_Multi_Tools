import os
import subprocess

from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

from bot import bot, bot_loop
from bot.helper.telegram_helper.filters import CustomFilters


async def sendMessage(message, text):
    return await message.reply(text=text, quote=True)


async def editMessage(message, text):
    try:
        await message.edit(text=text)
    except:
        pass


async def git_push_kernel_source(client, message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply("<b>Error:</b> Please reply to a zip file with the command.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("<b>Error:</b> Please provide a branch name.")
        return

    file_name = message.reply_to_message.document.file_name
    if not file_name.endswith(".zip"):
        await message.reply("<b>Error:</b> Only zip files are supported.")
        return

    GIT_BRANCH_NAME = args[1]
    GIT_USERNAME = "SN-Abdullah-Al-Noman"
    GIT_EMAIL = "snprotectserver12@gmail.com"
    GIT_REMOTE_ORIGIN = "https://github.com/SN-Abdullah-Al-Noman/Samsung_Kernel_Sources.git"
    GIT_ACCESS_TOKEN = "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"

    banner = "<b>Samsung Kernel to Git Push Bot By Al Noman</b>\n"
    status = await sendMessage(message, banner)

    banner += "\n<b>Downloading kernel source.</b>"
    await editMessage(status, banner)
    file_path = await client.download_media(message.reply_to_message.document)
    banner += " ☑️"
    await editMessage(status, banner)

    banner += "\n<b>Extracting kernel source.</b>"
    await editMessage(status, banner)
    
    os.makedirs(, exist_ok=True)

    subprocess.run(f"7z x '{file_path}' -o'{GIT_BRANCH_NAME}' -y", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.remove(file_path)
    banner += " ☑️"
    await editMessage(status, banner)

    files = os.listdir()
    if "Kernel.tar.gz" in files and "Platform.tar.gz" in files:
        await editMessage(status, "<b>Error:</b> Not a valid kernel source.")
        return

    banner += "\n<b>Configuring git credentials.</b>"
    await editMessage(status, banner)
    subprocess.run(["git", "config", "--global", "user.email", GIT_EMAIL], check=True)
    subprocess.run(["git", "config", "--global", "user.name", GIT_USERNAME], check=True)

    banner += " ☑️"
    await editMessage(status, banner)

    banner += "\n<b>Initializing git repository.</b>"
    await editMessage(status, banner)
    subprocess.run(["git", "init"], cwd=f"{GIT_BRANCH_NAME}", check=True)
    subprocess.run(["git", "add", "."], cwd=f"{GIT_BRANCH_NAME}", check=True)
    subprocess.run(["git", "commit", "-m", f"Initial commit {GIT_BRANCH_NAME}"], cwd=f"{GIT_BRANCH_NAME}", check=True)
    subprocess.run(["git", "branch", "-M", GIT_BRANCH_NAME], cwd=f"{GIT_BRANCH_NAME}", check=True)
    banner += " ☑️"
    await editMessage(status, banner)

    banner += "\n<b>Pushing repository to GitHub.</b>"
    await editMessage(status, banner)

    git_remote_url = f"https://{GIT_USERNAME}:{GIT_ACCESS_TOKEN}@github.com/SN-Abdullah-Al-Noman/Samsung_Kernel_Sources.git"
    
    subprocess.run(["git", "remote", "add", "origin", git_remote_url], cwd=f"{GIT_BRANCH_NAME}", check=True)
    subprocess.run(["git", "push", "-u", "origin", GIT_BRANCH_NAME], cwd=f"{GIT_BRANCH_NAME}", check=True)
    banner += " ☑️"
    await editMessage(status, banner)

    banner += f"\n\n<b>Kernel source pushed successfully to\n{GIT_REMOTE_ORIGIN.removesuffix('.git')}/tree/{GIT_BRANCH_NAME}</b>"
    await editMessage(status, banner)


bot.add_handler(MessageHandler(git_push_kernel_source, filters=command("git") & CustomFilters.owner))
