from pyrogram import Client, filters
from pyrogram.types import Message
from RyuzakiLib import Tiktok
from config import TIKTOK_WEB as tt, API_ID, API_HASH, BOT_TOKEN

client = Client(
    "TTK-BOT",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
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
