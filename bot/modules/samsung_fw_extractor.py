import io
import os
import shutil
import pickle
import subprocess
from functools import wraps

from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

from bot import bot, bot_loop, DRIVE_FOLDER_ID
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
        subprocess.run(['wget', '-O', 'archive.zip', '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"', f'{link}'], cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\nFailed: {e}."
        subprocess.run("rm -rf *", shell=True, cwd=DOWNLOAD_DIR)
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 8:</b> Uploading zip in google drive."
    await editMessage(status, banner)
    try:
        upload_in_drive("archive.zip", DOWNLOAD_DIR, DRIVE_FOLDER_ID)
        banner = f"\n{banner}\n\n<b>File Uploading Completed.</b>\nHere is file link : {file.get("id")}"
        await editMessage(status, banner)
    except Exception as e:
        banner = f"\n{banner}\nFailed: {e}."
        await editMessage(status, banner)
        subprocess.run("rm -rf *.zip", shell=True, cwd=DOWNLOAD_DIR)
        return

bot.add_handler(MessageHandler(samsung_fw_extract, filters=command("fw")))
