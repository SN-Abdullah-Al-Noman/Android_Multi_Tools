import os
import shutil
import subprocess
from functools import wraps

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

from bot import bot, bot_loop
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

def new_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return bot_loop.create_task(func(*args, **kwargs))

    return wrapper


@new_task
def upload_in_drive(file_name, file_path, DRIVE_FOLDER_ID):
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            raise Exception("No valid credentials available. You need to obtain new OAuth tokens.")

    drive_service = build('drive', 'v3', credentials=credentials)
    file_metadata = {'name': file_name, 'parents': [DRIVE_FOLDER_ID]}
    desired_speed_mbps = 400
    chunk_size = int(desired_speed_mbps * 1000000 / 8)
    media_body = MediaIoBaseUpload(io.BytesIO(open(file_path, 'rb').read()), mimetype='application/octet-stream', resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media_body, supportsAllDrives=True, fields='id').execute()
    print(f'File uploaded. File ID is: {file.get("id")}')


@new_task
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
        return

    banner = f"\n{banner}\nFirmware download complete.\n"
    await editMessage(status, banner)
    
    banner = f"\n{banner}\n<b>Step 1:</b> Extracting firmware zip."
    await editMessage(status, banner)
    try:
        subprocess.run('7z x fw.zip && rm -rf firmware.zip && rm -rf *.txt && for file in *.md5; do mv -- "$file" "${file%.md5}"; done', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\nFailed: {e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 2:</b> Extracting tar files."
    await editMessage(status, banner)
    try:
        subprocess.run('for file in *.tar; do tar -xvf "$file"; done', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run("find . -type f ! -name 'super.img.lz4' ! -name 'optics.img.lz4' ! -name 'prism.img.lz4' ! -name 'boot.img.lz4' -delete", shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf *.tar', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf meta-data', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 3:</b> Extracting lz4 files."
    await editMessage(status, banner)
    try:
        subprocess.run('for file in *.lz4; do lz4 -d "$file" "${file%.lz4}"; done', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 4:</b> Converting sparse super.img to raw super.img."
    await editMessage(status, banner)
    try:
        subprocess.run("simg2img super.img super_raw.img", shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run("rm -rf super.img", shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run("mv super_raw.img super.img", shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
            banner = f"\n{banner}\n{e}."
            await editMessage(status, banner)
            return

    banner = f"\n{banner}\n<b>Step 5:</b> Extracting all partitions from super.img"
    await editMessage(status, banner)
    try:
        subprocess.run('lpunpack super.img', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf super.img', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 6:</b> Compressing all img to xz level 9."
    await editMessage(status, banner)
    try:
        subprocess.run('for i in *.img; do 7z a -mx9 "${i%.*}.img.xz" "$i"; done && rm -rf *.img', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        subprocess.run('rm -rf *.img', shell=True, cwd=DOWNLOAD_DIR)
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 7:</b> Compressing all files into single zip."
    await editMessage(status, banner)
    try:
        subprocess.run('7z a -tzip -mx=9 archive.zip *', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 8:</b> Uploading zip in google drive."
    await editMessage(status, banner)
    upload_in_drive(archive.zip, DOWNLOAD_DIR, DRIVE_FOLDER_ID)
    banner = f"\n{banner}\n\n<b>File Uploading Completed.</b>\nHere is file link : {file.get("id")}"
    await editMessage(status, banner)
    subprocess.run("rm -rf *.zip", shell=True, cwd=DOWNLOAD_DIR)

bot.add_handler(MessageHandler(samsung_fw_extract, filters=command("fw")))
