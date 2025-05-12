import io
import os
import sys
import glob
import shutil
import pickle
import subprocess
from functools import wraps
from urllib.parse import urlparse, parse_qs

from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

from bot import bot, bot_loop, DRIVE_FOLDER_ID
from bot.helper.telegram_helper.filters import CustomFilters

DOWNLOAD_DIR = "work"


async def send_message(message, text):
    return await message.reply(text=text, quote=True)

async def edit_message(message, text):
    try:
        await message.edit(text=text)
    except Exception as e:
        print(f"Failed to edit message: {e}")


def new_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return bot_loop.create_task(func(*args, **kwargs))
    return wrapper


def load_credentials():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except Exception as e:
                raise Exception(f"Error refreshing credentials: {e}")
        else:
            raise Exception("No valid credentials available. You need to obtain new OAuth tokens.")
    return credentials


async def create_drive_folder(drive_service, folder_name, parent_folder_id):
    try:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    except Exception as e:
        raise Exception(f"Error creating folder in Google Drive: {e}")


@new_task
async def upload_in_drive(file_path, drive_folder_id):
    credentials = load_credentials()
    drive_service = build('drive', 'v3', credentials=credentials)

    file_metadata = {'name': os.path.basename(file_path), 'parents': [drive_folder_id]}
    with open(file_path, 'rb') as f:
        media_body = MediaIoBaseUpload(io.BytesIO(f.read()), mimetype='application/octet-stream', resumable=True)
    
    try:
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media_body,
            supportsAllDrives=True,
            fields='id'
        ).execute()
        return file
    except Exception as e:
        raise Exception(f"Error uploading file to Google Drive: {e}")


def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.stderr.strip()}")
        return None


@new_task
async def samsung_fw_download_upload(client, message):
    args = message.text.split()[1:]
    if len(args) != 3:
        await send_message(message, f"<b>Usage:</b> /fw MODEL CSC IMEI")
        return

    MODEL = args[0]
    CSC = args[1]
    IMEI = args[2]

    banner = f"<b>Samsung FW Downloader By Al Noman</b>\n"
    status = await send_message(message, banner)

    banner = f"{banner}\n<b>Fetching Latest Firmware.</b>"
    await edit_message(status, banner)

    version = run_command(f"python3 -m samloader -m {MODEL} -r {CSC} -i {IMEI} checkupdate 2>/dev/null")
    if version:
        banner = f"{banner}\n<b>Update found:</b>\n{version}\n\n<b>Firmware download started.</b>"
        await edit_message(status, banner)
    else:
        banner = f"{banner}\n<b>MODEL or REGION not found.</b>"
        await edit_message(status, banner)
        return
        
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
    os.makedirs(DOWNLOAD_DIR)

    download_command = f"python3 -m samloader -m {MODEL} -r {CSC} -i {IMEI} download -v {version} -O {DOWNLOAD_DIR}"
    if run_command(download_command) is None:
        banner = f"{banner}\n<b>Something Strange Happened. Did you enter the correct IMEI for your device MODEL?</b>"
        await edit_message(status, banner)
        return

    files = glob.glob(f"{DOWNLOAD_DIR}/*.enc*")
    if files:
        banner = f"{banner}\n<b>Firmware download completed.\nDecrypting firmware.</b>"
        await edit_message(status, banner)
        file_path = files[0]
        decrypt_command = f"python3 -m samloader -m {MODEL} -r {CSC} -i {IMEI} decrypt -v {version} -i {file_path} -o {DOWNLOAD_DIR}/firmware.zip"
        if run_command(decrypt_command) is None:
            banner = f"{banner}\n<b>Something Strange Happened.</b>"
            await edit_message(status, banner)
            return
        else:
            file_size = os.path.getsize(f"{DOWNLOAD_DIR}/firmware.zip")
            file_size_mb = file_size / (1024 * 1024)
            banner = f"{banner}\n<b>Firmware decrypted.\nFirmware size is :</b> {file_size_mb:.2f} MB\n"
            await edit_message(status, banner)
        os.remove(file_path)
    else:
        banner = f"{banner}\n<b>No encrypted file found for decryption.</b>"
        await edit_message(status, banner)
        return


    banner = f"{banner}\nCreating folder in Google Drive."
    await edit_message(status, banner)

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
    drive_folder_id = await create_drive_folder(drive_service, version, DRIVE_FOLDER_ID)

    banner = f"{banner}\n<b>Step 8:</b> Uploading all files to Google Drive."
    await edit_message(status, banner)
    for file_name in os.listdir(DOWNLOAD_DIR):
        if file_name.endswith('.zip'):
            file_path = os.path.join(DOWNLOAD_DIR, file_name)
            await upload_in_drive(file_path, drive_folder_id)

    banner = f"{banner}\n\n<b>Upload Completed.</b>\nFolder link: https://drive.google.com/drive/folders/{drive_folder_id}"
    await edit_message(status, banner)
    subprocess.run("rm -rf *", shell=True, cwd=DOWNLOAD_DIR)


bot.add_handler(MessageHandler(samsung_fw_download_upload, filters=command("sfwdu") & CustomFilters.owner))
