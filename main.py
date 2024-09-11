import logging
import time
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import *
from RyuzakiLib import Tiktok
from config import TIKTOK_WEB as tt, API_ID, API_HASH, BOT_TOKEN
import hashlib

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)

WELCOME_TEXT = """
Halo {}
Saya adalah bot untuk mengunduh video tiktok di telegram.

Saya dapat mengunduh video dengan tanda air atau tanpa tanda air dan mengunduh audio dari url. Kirimkan saja saya url tiktok.
"""

client = Client(
    "TTK-BOT",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

link_storage = {}

def generate_callback_data(user_id, query):
    identifier = hashlib.md5(query.encode()).hexdigest()
    callback_data = f"audiodownload_{user_id}_{identifier}"
    link_storage[callback_data] = query
    return callback_data

@client.on_message(filters.command("start") & filters.private)
async def welcome_start(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="📢 Saluran Bot",
                    url="https://t.me/RendyProjects"
                )
            ]
        ]
    )
    await message.reply_text(
        WELCOME_TEXT.format(message.from_user.first_name),
        reply_markup=keyboard
    )

@client.on_callback_query(filters.regex("^audiodownload_"))
async def callback_button(client: Client, cb: CallbackQuery):
    try:
        data = cb.data
        user_id = cb.from_user.id
        query = link_storage.get(data)
        if query:
            response = await Tiktok.download(tt, query)
            await client.send_audio(user_id, response[1])
            await cb.answer("Audio sent successfully!")
        else:
            await cb.answer("Invalid or expired link.", show_alert=True)
    except Exception as e:
        await cb.answer(f"Error: {str(e)}", show_alert=True)

@client.on_message(filters.text & filters.private)
async def all_downloader(client: Client, message: Message):
    if message.text:
        query = message.text.strip()
        if not (
            query.startswith("https://vt.tiktok.com/")
            or query.startswith("https://www.tiktok.com/")
            or query.startswith("https://youtu.be/")
        ):
            return await message.reply_text("Invalid link")

        if query.startswith("https://vt.tiktok.com/") or query.startswith("https://www.tiktok.com/"):
            callback_data = generate_callback_data(message.from_user.id, query)
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Audio Download",
                            callback_data=callback_data
                        )
                    ]
                ]
            )
            try:
                dll = await message.reply_text("Processing....")
                await message.delete()
                response = await Tiktok.download(tt, query)
                await message.reply_video(response[0], reply_markup=keyboard)
                await dll.delete()
            except Exception as e:
                await dll.delete()
                await message.reply_text(f"Error: {str(e)}")
        elif query.startswith("https://youtu.be/"):
            pro = await message.reply_text("Checking ...")
            status, url = YoutubeDriver.check_url(query)
            if not status:
                return await pro.edit_text(url)
            await pro.edit_text("🎼 __Downloading video ...__")
            try:
                with YoutubeDL(YoutubeDriver.video_options()) as ytdl:
                    yt_data = ytdl.extract_info(url, True)
                    yt_file = yt_data["id"]
                upload_text = f"**⬆️ 𝖴𝗉𝗅𝗈𝖺𝖽𝗂𝗇𝗀 𝖲𝗈𝗇𝗀 ...** \n\n**𝖳𝗂𝗍𝗅𝖾:** `{yt_data['title'][:50]}`\n**𝖢𝗁𝖺𝗇𝗇𝖾𝗅:** `{yt_data['channel']}`"
                await pro.edit_text(upload_text)
                response = requests.get(f"https://i.ytimg.com/vi/{yt_data['id']}/hqdefault.jpg")
                with open(f"{yt_file}.jpg", "wb") as f:
                    f.write(response.content)
                await message.reply_video(
                    f"{yt_file}.mp4",
                    caption=f"**🎧 𝖳𝗂𝗍𝗅𝖾:** {yt_data['title']} \n\n**👀 𝖵𝗂𝖾𝗐𝗌:** `{yt_data['view_count']}` \n**⌛ 𝖣𝗎𝗋𝖺𝗍𝗂𝗈𝗇:** `{secs_to_mins(int(yt_data['duration']))}`",
                    duration=int(yt_data["duration"]),
                    thumb=f"{yt_file}.jpg",
                    progress=progress,
                    progress_args=(
                        pro,
                        time.time(),
                        upload_text,
                    ),
                )
                await pro.delete()
            except Exception as e:
                return await pro.edit_text(f"**🍀 Video not Downloaded:** `{e}`")
            try:
                os.remove(f"{yt_file}.jpg")
                os.remove(f"{yt_file}.mp4")
            except:
                pass
        else:
            await message.reply_text("Link format not recognized.")


client.run()
