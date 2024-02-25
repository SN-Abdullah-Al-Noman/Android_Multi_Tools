from dotenv import load_dotenv
from pymongo import MongoClient
from tzlocal import get_localzone
from pyrogram import Client as tgClient, enums
from os import remove as osremove, path as ospath, environ
from logging import getLogger, FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info, warning as log_warning


basicConfig(format="[%(asctime)s] [%(levelname)s] - %(message)s", #  [%(filename)s:%(lineno)d]
            datefmt="%d-%b-%y %I:%M:%S %p",
            handlers=[FileHandler('log.txt'), StreamHandler()],
            level=INFO)

user_data = {}
LOGGER = getLogger(__name__)
load_dotenv('config.env', override=True)

BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    log_error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

bot_id = BOT_TOKEN.split(':', 1)[0]

TELEGRAM_API = environ.get('TELEGRAM_API', '')
if len(TELEGRAM_API) == 0:
    log_error("TELEGRAM_API variable is missing! Exiting now")
    exit(1)
else:
    TELEGRAM_API = int(TELEGRAM_API)

TELEGRAM_HASH = environ.get('TELEGRAM_HASH', '')
if len(TELEGRAM_HASH) == 0:
    log_error("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)
    
OWNER_ID = environ.get('OWNER_ID', '')
if len(OWNER_ID) == 0:
    log_error("OWNER_ID variable is missing! Exiting now")
    exit(1)
else:
    OWNER_ID = int(OWNER_ID)  
    
DATABASE_URL = environ.get('DATABASE_URL', '') 
if len(DATABASE_URL) == 0: 
    DATABASE_URL = '' 

DATABASE_NAME = environ.get('DATABASE_NAME', '')
if len(DATABASE_NAME) == 0:
    DATABASE_NAME = 'mltb'
            
if DATABASE_URL:
    conn = MongoClient(DATABASE_URL)
    db = conn.get_database(DATABASE_NAME)
    config_dict = db.settings.config.find_one({'_id': bot_id})
else:
    config_dict = {}

FSUB_IDS = environ.get('FSUB_IDS', '')
if len(FSUB_IDS) == 0:
    FSUB_IDS = ''

SIM_INFO_CHECKER_CHATS = environ.get('SIM_INFO_CHECKER_CHATS', '')
if len(SIM_INFO_CHECKER_CHATS) != 0:
    aid = SIM_INFO_CHECKER_CHATS.split()
    for id_ in aid:
        user_data[int(id_.strip())] = {'is_sim_info_checker': True}
           
UPSTREAM_REPO = environ.get('UPSTREAM_REPO', '')
if len(UPSTREAM_REPO) == 0:
    UPSTREAM_REPO = ''

UPSTREAM_BRANCH = environ.get('UPSTREAM_BRANCH', '')
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = 'master'


config_dict = {'BOT_TOKEN': BOT_TOKEN,
               'DATABASE_URL': DATABASE_URL,
               'FSUB_IDS': FSUB_IDS,
               'OWNER_ID': OWNER_ID,
               'SIM_INFO_CHECKER_CHATS': SIM_INFO_CHECKER_CHATS,
               'TELEGRAM_API': TELEGRAM_API,
               'TELEGRAM_HASH': TELEGRAM_HASH,
               'UPSTREAM_REPO': UPSTREAM_REPO,
               'UPSTREAM_BRANCH': UPSTREAM_BRANCH}
               
               
log_info("Creating client from BOT_TOKEN") 
bot = tgClient('bot', TELEGRAM_API, TELEGRAM_HASH, bot_token=BOT_TOKEN, workers=1000, parse_mode=enums.ParseMode.HTML).start() 
bot_loop = bot.loop 
bot_name = bot.me.username 
