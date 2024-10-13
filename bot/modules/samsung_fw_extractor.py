import os
import shutil
import subprocess

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters


DOWNLOAD_DIR = "./f/"
files_to_keep = ["boot.img.lz4", "super.img.lz4"]

async def sendMessage(message, text):
    return await message.reply(text=text, quote=True)


async def editMessage(message, text):
    try:
        await message.edit(text=text)
    except:
        pass


async def samsung_fw_extract(client, message):
    args = message.text.split()
    link = args[1] if len(args) > 1 else ''
    if len(link) == 0 and (reply_to := message.reply_to_message):
        link = reply_to.text.split(maxsplit=1)[0].strip()
    
    if not link:
        return await message.reply(f"Please reply any samsung firmware download link")

    banner = f"<b>Samsung FW Extractor By Al Noman</b>\n"
    status = await sendMessage(message, banner)

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    banner = f"\n{banner}\nFirmware downloading."
    await editMessage(status, banner)

    try:
        subprocess.run(['wget', '-O', 'fw.zip', '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"', f'{link}'], cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\nFailed: {e}."
        await editMessage(status, banner)

    banner = f"\n{banner}\nFirmware download complete.\n"
    await editMessage(status, banner)
    
    banner = f"\n{banner}\n<b>Step 1:</b> Extracting firmware zip."
    await editMessage(status, banner)
    try:
        subprocess.run(['7z', 'x', 'fw.zip'], cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\nFailed: {e}."
        await editMessage(status, banner)

    for file in os.listdir(DOWNLOAD_DIR):
        if file.endswith(".tar.md5"):
            old_path = os.path.join(DOWNLOAD_DIR, file)
            new_name = os.path.join(DOWNLOAD_DIR, file.replace(".md5", ""))
            os.rename(old_path, new_name)

    banner = f"\n{banner}\n<b>Step 2:</b> Extracting tar files."
    await editMessage(status, banner)
    for file in os.listdir(DOWNLOAD_DIR):
        try:
            if file.endswith(".tar"):
                subprocess.run(["7z", "x", f"{DOWNLOAD_DIR}/{file}", f"-o{DOWNLOAD_DIR}", "-aoa"])
        except Exception as e:
            banner = f"\n{banner}\n{e}."
            await editMessage(status, banner)
            return


    banner = f"\n{banner}\n<b>Step 3:</b> Extracting lz4 files."
    await editMessage(status, banner)
    lz4_files = [file for file in os.listdir(DOWNLOAD_DIR) if file.endswith(".lz4")]
    for file in lz4_files:
        lz4_file_path = os.path.join(DOWNLOAD_DIR, file)
        subprocess.run(["lz4", "-d", lz4_file_path, f"-o{DOWNLOAD_DIR}"])

    banner = f"\n{banner}\n<b>Step 4:</b> Converting sparse super.img to raw super.img."
    await editMessage(status, banner)
    subprocess.run("simg2img super.img super_raw.img", shell=True, cwd=DOWNLOAD_DIR)
    subprocess.run("rm -rf super.img", shell=True, cwd=DOWNLOAD_DIR)
    subprocess.run("mv super_raw.img super.img", shell=True, cwd=DOWNLOAD_DIR)

    banner = f"\n{banner}\n<b>Step 5:</b> Extracting all partitions from super.img"
    await editMessage(status, banner)
    subprocess.run("lpunpack super.img", shell=True, cwd=DOWNLOAD_DIR)
    subprocess.run("rm -rf super.img", shell=True, cwd=DOWNLOAD_DIR)

    banner = f"\n{banner}\n<b>Step 6:</b> Compressing all img to xz level 9."
    await editMessage(status, banner)
    try:
        subprocess.run('for i in *.img; do 7z a -mx9 "${i%.*}.img.xz" "$i"; done && rm -rf *.img', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        subprocess.run("rm -rf *.img", shell=True, cwd=DOWNLOAD_DIR)
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 7:</b> Compressing all files into single zip."
    await editMessage(status, banner)
    try:
        subprocess.run("7z a -tzip -mx=9 archive.zip *", shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 8:</b> Uploading zip in google drive."
    await editMessage(status, banner)
    banner = f"\n{banner}\n\n<b>File Uploading Completed.</b>\nHere is file link."
    await editMessage(status, banner)
    subprocess.run("rm -rf *", shell=True, cwd=DOWNLOAD_DIR)

bot.add_handler(MessageHandler(samsung_fw_extract, filters=command("fw")))
