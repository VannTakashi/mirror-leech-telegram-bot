from time import time
from pyrogram.enums import ParseMode
from telegram.helpers import mention_html

from ..helper.ext_utils.bot_utils import new_task
from ..helper.telegram_helper.button_build import ButtonMaker
from ..helper.telegram_helper.message_utils import send_message, edit_message, send_file
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.bot_commands import BotCommands

@new_task
async def start(_, message):
    user = message.from_user
    mention = mention_html(user.id, user.full_name)

    buttons = ButtonMaker()
    buttons.url_button("📦 Repo", "https://www.github.com/VannTakashi/mirror-leech-telegram-bot")
    buttons.url_button("👤 Maintainer", "https://t.me/panzzxz")
    reply_markup = buttons.build_menu(2)

    if await CustomFilters.authorized(_, message):
        start_string = f"""
Halo {mention}! 👋

🤖 <b>Selamat datang di Bot Mirror Leech!</b>

Bot ini dapat membantu kamu:
🔗 Mirror dari: direct link, file Telegram, torrent, NZB, atau rclone cloud
📤 Upload ke: Google Drive, rclone cloud lain, atau balik ke Telegram

Ketik <code>/{BotCommands.HelpCommand}</code> untuk melihat semua perintah yang tersedia.

Selamat mencoba dan semoga bermanfaat! 🚀
"""
        await send_message(message, start_string, reply_markup, parse_mode=ParseMode.HTML)
    else:
        warning_msg = f"""
Halo {mention}! 👋

Bot ini hanya bisa digunakan oleh user yang terotorisasi.

⚠️ <b>Kamu belum terotorisasi.</b>
Silakan deploy sendiri bot ini via repo berikut:

👉 <a href="https://www.github.com/VannTakashi/mirror-leech-telegram-bot">mirror-leech-telegram-bot</a>
"""
        await send_message(message, warning_msg, reply_markup, parse_mode=ParseMode.HTML)

@new_task
async def ping(_, message):
    start_time = int(round(time() * 1000))
    reply = await send_message(message, "Starting Ping")
    end_time = int(round(time() * 1000))
    await edit_message(reply, f"{end_time - start_time} ms")

@new_task
async def log(_, message):
    await send_file(message, "log.txt")
