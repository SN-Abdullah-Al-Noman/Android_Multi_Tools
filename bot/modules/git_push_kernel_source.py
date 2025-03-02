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
        await message.reply(f"<b>Error:</b> Please reply to a zip file with the command.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply(f"<b>Error:</b> Please provide a branch name.")
        return
    GIT_BRANCH_NAME = args[1]
    
    file_name = message.reply_to_message.document.file_name
    if not file_name.endswith(".zip"):
        await message.reply(f"<b>Error:</b> Only zip files are supported.")
        return

    GIT_USERNAME = "SN-Abdullah-Al-Noman"
    GIT_EMAIL = "snprotectserver12@gmail.com"
    GIT_REMOTE_ORIGIN = "https://github.com/SN-Abdullah-Al-Noman/Samsung_Kernel_Sources.git"
    GIT_ACCESS_TOKEN = "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"
    
    banner = f"<b>Samsung Kernel to Git Push Bot By Al Noman</b>\n"
    status = await sendMessage(message, banner)
    
    banner += f"\n<b>Downloading kernel source.</b>"
    await editMessage(status, banner)
    file_path = await client.download_media(message.reply_to_message.document)
    banner += " ☑️"
    await editMessage(status, banner)

    banner += f"\n<b>Extracting kernel source.</b>"
    await editMessage(status, banner)
    extract_path = file_path.replace(".zip", "")
    os.makedirs(extract_path, exist_ok=True)
    subprocess.run(f"7z x '{file_path}' -o'{extract_path}' -y", shell=True)
    os.remove(file_path)

    banner += f"<b>File extracted successfully.</b>\nPath: <code>{extract_path}</code>\nBranch: <code>{GIT_BRANCH_NAME}</code>\n"
    await editMessage(status, banner)

    banner += f"\n<b>Configuring git credentials.</b>"
    await editMessage(status, banner)

    subprocess.run(["git", "config", "--global", "user.email", GIT_EMAIL])
    subprocess.run(["git", "config", "--global", "user.name", GIT_USERNAME])
    subprocess.run(["git", "config", "--global", "init.defaultBranch", GIT_BRANCH_NAME])
    subprocess.run(["git", "config", "--global", "credential.helper", "store"])
    subprocess.run(f'printf "\\nhttps://{GIT_USERNAME}:{GIT_ACCESS_TOKEN}@github.com" >> ~/.git-credentials', shell=True, check=True)
    banner += " ☑️"
    await editMessage(status, banner)


    banner += f"\n<b>Extracting kernel source.</b>"
    await editMessage(status, banner)
    subprocess.run(["rm", "-rf", f"{GIT_BRANCH_NAME}"])
    subprocess.run(["mkdir", "-p", f"{GIT_BRANCH_NAME}"])
    subprocess.run(["tar", "-xzvf", "Kernel.tar.gz", "-C", f"{GIT_BRANCH_NAME}"])
    subprocess.run(["clear"])
    banner += " ☑️"
    await editMessage(status, banner)


    banner += f"\n<b>Initializing git repository.</b>"
    await editMessage(status, banner)
    subprocess.run(["git", "init"], cwd=f"{GIT_BRANCH_NAME}")
    subprocess.run(["git", "add", "."], cwd=f"{GIT_BRANCH_NAME}")
    subprocess.run(["git", "commit", "-m", f"Initial commit {GIT_BRANCH_NAME}"], cwd=f"{GIT_BRANCH_NAME}")
    subprocess.run(["git", "branch", "-M", f"{GIT_BRANCH_NAME}"], cwd=f"{GIT_BRANCH_NAME}")
    subprocess.run(["clear"])
    banner += " ☑️"
    await editMessage(status, banner)


    if os.path.exists(f"{GIT_BRANCH_NAME}/drivers/misc/mediatek/connectivity"):
        banner += "\n<b>Extracting & adding kernel drivers.</b>"
        await editMessage(status, banner)
        subprocess.run(["rm", "-rf", "Platform"])
        subprocess.run(["mkdir", "-p", "Platform"])
        subprocess.run(["tar", "-xzvf", "Platform.tar.gz", "-C", "Platform"])
        
        if os.path.exists("Platform/vendor/mediatek/kernel_modules/connectivity"):
            subprocess.run(f"cp -r Platform/vendor/mediatek/kernel_modules/connectivity/* {GIT_BRANCH_NAME}/drivers/misc/mediatek/connectivity/", shell=True)
            subprocess.run(["git", "add", "."], cwd=f"{GIT_BRANCH_NAME}")
            subprocess.run(["git", "commit", "-m", "Add Bluetooth, FM Radio, GPS, Wifi driver."], cwd=f"{GIT_BRANCH_NAME}")
            banner += " ☑️"
            await editMessage(status, banner)
        
            banner += f"\n<b>Updating driver import locations.</b>"
            await editMessage(status, banner)
            subprocess.run(f'find "{GIT_BRANCH_NAME}/drivers/misc/mediatek/connectivity" -type f -exec sed -i '
                '-e "s|vendor/mediatek/kernel_modules/connectivity/|$(srctree)/drivers/misc/mediatek/connectivity/|g" '
                '-e "s|(TOP)/vendor/mediatek/kernel_modules/connectivity/|(srctree)/drivers/misc/mediatek/connectivity/|g" '
                '-e "s|(TOP)/$(srctree)/drivers/misc/mediatek/connectivity/|(srctree)/drivers/misc/mediatek/connectivity/|g" {} +', 
                shell=True)
            subprocess.run(["git", "add", "."], cwd=f"{GIT_BRANCH_NAME}")
            subprocess.run(["git", "commit", "-m", "Update Bluetooth, FM Radio, GPS, Wifi drivers import location."], cwd=f"{GIT_BRANCH_NAME}")
            banner += " ☑️"
            await editMessage(status, banner)


    banner += f"\n<b>Disabling auto add localversion.</b>"
    await editMessage(status, banner)
    DEF_CONFIG = subprocess.run("awk '/make .*defconfig/ {print $NF}' build_kernel.sh", shell=True, capture_output=True, text=True, cwd=f"{GIT_BRANCH_NAME}").stdout.strip()
    subprocess.run(f'sed -i "/^CONFIG_LOCALVERSION_AUTO=/c\\CONFIG_LOCALVERSION_AUTO=n" arch/arm64/configs/{DEF_CONFIG}', shell=True, cwd=f"{GIT_BRANCH_NAME}")
    subprocess.run([r"sed", r"-i", r'/res="\$res\${scm:++}"/d', r"scripts/setlocalversion"], shell=False, cwd=f"{GIT_BRANCH_NAME}")
    subprocess.run(["git", "add", "."], cwd=f"{GIT_BRANCH_NAME}")
    subprocess.run(["git", "commit", "-m", "Disable auto add extra localversion."], cwd=f"{GIT_BRANCH_NAME}")
    banner += " ☑️"
    await editMessage(status, banner)


    banner += f"\n<b>Adding kernel information.</b>"
    await editMessage(status, banner)
    subprocess.run(f'sed -i "s|^CONFIG_LOCALVERSION=.*|CONFIG_LOCALVERSION=\\"Atrocious Enforcing Kernel V:1 {GIT_BRANCH_NAME}\\"|" 'f'arch/arm64/configs/{DEF_CONFIG}', shell=True, cwd=f"{GIT_BRANCH_NAME}")
    subprocess.run(["git", "add", "."], cwd=f"{GIT_BRANCH_NAME}")
    subprocess.run(["git", "commit", "-m", "Kernel Information."], cwd=f"{GIT_BRANCH_NAME}")
    banner += " ☑️"
    await editMessage(status, banner)


    banner += f"\n<b>Pushing repository to GitHub.</b>"
    await editMessage(status, banner)
    subprocess.run(["git", "remote", "add", "origin", f"{GIT_REMOTE_ORIGIN}"], cwd=f"{GIT_BRANCH_NAME}")
    subprocess.run(["git", "push", "-u", "origin", f"{GIT_BRANCH_NAME}"], cwd=f"{GIT_BRANCH_NAME}")
    banner += " ☑️"
    await editMessage(status, banner)

    banner += f"\n\n<b>Kernel source pushed successfully to\n{GIT_REMOTE_ORIGIN.removesuffix('.git')}/tree/{GIT_BRANCH_NAME}</b>"
    await editMessage(status, banner)


bot.add_handler(MessageHandler(git_push_kernel_source, filters=command("git") & CustomFilters.owner))
