import logging
import logging.config
import os
import asyncio
from pyrogram import Client, filters, __version__  # নিশ্চিত করুন যে 'filters' আমদানি করা হয়েছে
from pyrogram.raw.all import layer
from aiohttp import web
from lazybot import LazyPrincessBot
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from plugins import web_server
from util.keepalive import ping_server
from lazybot.clients import initialize_clients

# Logging configuration
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

PORT = "8080"
LazyPrincessBot.start()

# Auto delete function added
@LazyPrincessBot.on_message(filters.private | filters.group)  # 'filters' সঠিকভাবে ব্যবহার করুন
async def auto_delete(client, message):
    await asyncio.sleep(10)  # ১০ সেকেন্ড পর মেসেজ ডিলিট হবে
    await client.delete_messages(chat_id=message.chat.id, message_ids=message.message_id)

async def Lazy_start():
    print('\n')
    print('Initializing Telegram Bot')
    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)
    bot_info = await LazyPrincessBot.get_me()
    LazyPrincessBot.username = bot_info.username
    await initialize_clients()
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    b_users, b_chats, lz_verified = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    temp.LAZY_VERIFIED_CHATS = lz_verified
    await Media.ensure_indexes()
    me = await LazyPrincessBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    LazyPrincessBot.username = '@' + me.username
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0" if ON_HEROKU else BIND_ADRESS
    await web.TCPSite(app, bind_address, PORT).start()
    logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR)
    await idle()

if __name__ == '__main__':
    try:
        asyncio.run(Lazy_start())  # asyncio.get_event_loop() পরিবর্তন করে asyncio.run() ব্যবহার করুন
        logging.info('-----------------------🧐 Service running in Lazy Mode 😴-----------------------')
    except KeyboardInterrupt:
        logging.info('-----------------------😜 Service Stopped Sweetheart 😝-----------------------')
