from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from RyuzakiLib import Tiktok
from config import TIKTOK_WEB as tt, API_ID, API_HASH, BOT_TOKEN

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

@client.on_message(filters.text & filters.private)
async def tiktok_downloader(client: Client, message: Message):
    if message.text:
        try:
            query = message.text
            dll = await message.reply_text("Processing....")
            response = Tiktok(tt, query)
            await message.reply_video(response[0])
            await dll.delete()
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")

client.run()
