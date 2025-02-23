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
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload

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
async def samsung_fw_extract(client, message):
    args = message.text.split()[1:]
    if len(args) != 3:
        await send_message(message, f"<b>Usage:</b> /fw MODEL CSC IMEI")
        return

    MODEL = args[0]
    CSC = args[1]
    IMEI = args[2]

    banner = f"<b>Samsung FW Extractor By Al Noman</b>\n"
    status = await send_message(message, banner)

    banner = f"\n<b>{banner}\nFetching Latest Firmware.</b>"
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
        banner = f"{banner}\n<b>Something Strange Happened. Did you enter the correct IMEI for your device MODEL ?</b>"
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
            banner = f"{banner}\n<b>Firmware decrypted. Firmware size is :</b> {file_size_mb:.2f} 
            await edit_message(status, banner)
        os.remove(file_path)
    else:
        banner = f"{banner}\n<b>No encrypted file found for decryption.</b>"
        edit_message(status, banner)
        return

    banner = f"{banner}\nFirmware size is.</b>"
    await edit_message(status, banner)


    banner = f"\n{banner}\n\n<b>Step 1:</b> Extracting firmware zip."
    await edit_message(status, banner)
    try:
        subprocess.run('7z x firmware.zip && rm -rf firmware.zip && rm -rf *.txt && for file in *.md5; do mv -- "$file" "${file%.md5}"; done', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -f BL*tar.md5', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -f CP*tar.md5', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -f CSC*tar.md5', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -f HOME*tar.md5', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\nFailed: {e}."
        await edit_message(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 2:</b> Extracting tar files."
    await edit_message(status, banner)
    try:
        subprocess.run('for file in *.tar; do tar -xvf "$file"; done', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run("find . -type f ! -name 'super.img.lz4' ! -name 'optics.img.lz4' ! -name 'prism.img.lz4' ! -name 'boot.img.lz4' -delete", shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf *.tar', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf meta-data', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await edit_message(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 3:</b> Extracting lz4 files."
    await edit_message(status, banner)
    try:
        subprocess.run('for file in *.lz4; do lz4 -d "$file" "${file%.lz4}"; done', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await edit_message(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 4:</b> Converting sparse super.img to raw super.img."
    await edit_message(status, banner)
    try:
        subprocess.run("simg2img super.img super_raw.img", shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run("rm -rf super.img", shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run("mv super_raw.img super.img", shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await edit_message(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 5:</b> Extracting all partitions from super.img"
    await edit_message(status, banner)
    try:
        subprocess.run('lpunpack super.img', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf super.img', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf vendor.img', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf vendor_dlkm.img', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        banner = f"\n{banner}\n{e}."
        await edit_message(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 6:</b> Compressing all img to xz level 9."
    await edit_message(status, banner)
    try:
        subprocess.run('rm -rf boot.img', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf optics.img', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('rm -rf prism.img', shell=True, cwd=DOWNLOAD_DIR)
        subprocess.run('for i in *.img; do 7z a -mx9 "${i%.*}.img.xz" "$i"; done && rm -rf *.img', shell=True, cwd=DOWNLOAD_DIR)
    except Exception as e:
        subprocess.run('rm -rf *.img', shell=True, cwd=DOWNLOAD_DIR)
        banner = f"\n{banner}\n{e}."
        await edit_message(status, banner)
        return

    banner = f"\n{banner}\n<b>Step 7:</b> Creating folder in Google Drive."
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

    banner = f"\n{banner}\n<b>Step 8:</b> Uploading all files in google drive."
    await edit_message(status, banner)
    for file_name in os.listdir(DOWNLOAD_DIR):
        if file_name.endswith('.xz'):
            file_path = os.path.join(DOWNLOAD_DIR, file_name)
            await upload_in_drive(file_path, drive_folder_id)

    banner = f"\n{banner}\n\n<b>Upload Completed.</b>\nFolder link: https://drive.google.com/drive/folders/{drive_folder_id}"
    await edit_message(status, banner)
    subprocess.run("rm -rf *", shell=True, cwd=DOWNLOAD_DIR)

bot.add_handler(MessageHandler(samsung_fw_extract, filters=command("fw") & CustomFilters.owner))
