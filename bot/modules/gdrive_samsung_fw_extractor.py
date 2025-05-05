import io
import os
import shutil
import pickle
import subprocess
from functools import wraps
from urllib.parse import urlparse, parse_qs

from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload

from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

from bot import bot, bot_loop, DRIVE_FOLDER_ID
from bot.helper.telegram_helper.filters import CustomFilters


DOWNLOAD_DIR = "work"
shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
os.makedirs(DOWNLOAD_DIR)


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


def load_credentials():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            raise Exception("No valid credentials available. You need to obtain new OAuth tokens.")

    return credentials


def extract_file_id_from_link(link):
    parsed_url = urlparse(link)
    if "drive.google.com" in parsed_url.netloc:
        if "id=" in parsed_url.query:
            query_params = parse_qs(parsed_url.query)
            return query_params.get("id", [None])[0]
        elif "/d/" in parsed_url.path:
            return parsed_url.path.split("/d/")[1].split("/")[0]
    raise ValueError("Invalid Google Drive link format")


async def download_from_google_drive(link, destination):
    credentials = load_credentials()
    drive_service = build('drive', 'v3', credentials=credentials)
    
    file_id = extract_file_id_from_link(link)
    request = drive_service.files().get_media(fileId=file_id)
    with open(destination, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
    return destination


async def create_drive_folder(drive_service, folder_name, parent_folder_id):
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')


@new_task
async def upload_in_drive(file_path, drive_folder_id):
    credentials = load_credentials()
    drive_service = build('drive', 'v3', credentials=credentials)

    file_metadata = {'name': os.path.basename(file_path), 'parents': [drive_folder_id]}
    with open(file_path, 'rb') as f:
        media_body = MediaIoBaseUpload(io.BytesIO(f.read()), mimetype='application/octet-stream', resumable=True)
    
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media_body,
        supportsAllDrives=True,
        fields='id'
    ).execute()
    return file


@new_task
async def samsung_fw_extract(client, message):
    args = message.text.split()
    folder_name = args[1] if len(args) > 1 else ''
    link = args[2] if len(args) > 2 else ''

    if not folder_name or not link:
        return await message.reply("Please provide a folder_name and link. Usage: /drivefw S24 www.sm_fw.com")

    banner = f"<b>Samsung FW Extractor By Al Noman</b>\n"
    status = await sendMessage(message, banner)

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    banner = f"\n{banner}\nFirmware downloading."
    await editMessage(status, banner)
    try:
        if "drive.google.com" in link:
            file_path = os.path.join(DOWNLOAD_DIR, 'fw.zip')
            await download_from_google_drive(link, file_path)
        else:
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
        subprocess.run('rm -f BL*tar.md5 CP*tar.md5 CSC*tar.md5 HOME*tar.md5', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\nFailed: {e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 2:</b> Extracting tar files."
    await editMessage(status, banner)
    try:
        subprocess.run('for file in *.tar; do tar -xvf "$file"; done', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run("find . -type f ! -name 'super.img.lz4' ! -name 'optics.img.lz4' ! -name 'prism.img.lz4' ! -name 'boot.img.lz4' -delete", shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf *.tar meta-data', shell=True, cwd=DOWNLOAD_DIR)
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
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 6:</b> Compressing all img to xz level 9."
    await editMessage(status, banner)
    try:
        subprocess.run('rm -rf boot.img optics.img prism.img system_dlkm.img vendor_dlkm.img vendor.img', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('for i in *.img; do 7z a -mx9 "${i%.*}.img.xz" "$i"; done && rm -rf *.img', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        subprocess.run('rm -rf *.img', shell=True, cwd=DOWNLOAD_DIR)
        banner = f"\n{banner}\n{e}."
        await editMessage(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 7:</b> Creating folder in Google Drive."
    await editMessage(status, banner)

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
    drive_folder_id = await create_drive_folder(drive_service, folder_name, DRIVE_FOLDER_ID)

    banner = f"\n{banner}\n<b>Step 8:</b> Uploading all files in google drive."
    await editMessage(status, banner)
    for file_name in os.listdir(DOWNLOAD_DIR):
        if file_name.endswith('.xz'):
            file_path = os.path.join(DOWNLOAD_DIR, file_name)
            await upload_in_drive(file_path, drive_folder_id)

    banner = f"\n{banner}\n\n<b>Upload Completed.</b>\nFolder link: https://drive.google.com/drive/folders/{drive_folder_id}"
    await editMessage(status, banner)
    subprocess.run("rm -rf *", shell=True, cwd=DOWNLOAD_DIR)

bot.add_handler(MessageHandler(samsung_fw_extract, filters=command("drivefw") & CustomFilters.owner))
