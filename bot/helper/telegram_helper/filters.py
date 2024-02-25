#!/usr/bin/env python3
from pyrogram.filters import create

from bot import user_data, OWNER_ID


class CustomFilters:

    async def owner_filter(self, client, update):
        user = update.from_user or update.sender_chat
        uid = user.id
        return uid == OWNER_ID

    owner = create(owner_filter)

    async def sim_info_checker_chats(self, _, message):
        user = message.from_user or message.sender_chat
        uid = user.id
        chat_id = message.chat.id
        return bool(uid == OWNER_ID or (uid in user_data and (user_data[uid].get('is_sim_info_checker', False))))

    sim_info_checker_chats = create(sim_info_checker_chats)
