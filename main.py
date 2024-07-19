import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from RyuzakiLib import Tiktok
from config import TIKTOK_WEB as tt, API_ID, API_HASH, BOT_TOKEN

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
    data = cb.data.split("_")
    data_test = cb.data.split("|")[1]
    user_id = int(data[1])
    link = str(data_test[1])
    response = Tiktok.download(tt, link)
    await client.send_audio(user_id, response[1])

@client.on_message(filters.text & filters.private)
async def tiktok_downloader(client: Client, message: Message):
    if message.text:
        query = message.text
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Audio Download",
                        callback_data=f"audiodownload_{message.from_user.id}|{query}"
                    )
                ]
            ]
        )
        try:
            dll = await message.reply_text("Processing....")
            await message.delete()
            response = Tiktok.download(tt, query)
            await message.reply_video(response[0], reply_markup=keyboard)
            await dll.delete()
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
            await dll.delete()

client.run()
