TOKEN = '7095597855:AAEwkWdxvEoNq2jRSLy6fIMv17P9GSIEa1Y'
import asyncio
import re
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatMemberUpdated
import aiohttp

API_DOMAINS_URL = "http://127.0.0.1:8000/api/domains/"
API_MESSAGE_URL = "http://127.0.0.1:8000/api/save_message/"

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)  # <--- BU YERDA BOT ARGUMENTINI KIRITDIK

# Domenlar ro‘yxatini olish uchun funksiya
async def get_domains():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://127.0.0.1:8000/api/domains/") as resp:
            if resp.status == 200:
                data = await resp.json()
                return [d for d in data]
    return []


# Xabarlarni tekshirish uchun handler
@dp.message_handler()  # Xabarlarni qayta ishlash uchun handler
async def check_message(message: types.Message):
    domains = await get_domains()
    user = message.from_user
    chat = message.chat
    message_text = message.text or ""
    
    # Domenni tekshirish
    found_domain = None
    for domain in domains:
        if domain in message_text:
            found_domain = domain
            break

    # Fayl turi tekshirish (.apk)
    file_type = None
    if message.document:
        if message.document.file_name.endswith(".apk"):
            file_type = "apk"

    # Agar domen yoki .apk fayl bo‘lsa, API-ga yuborish va foydalanuvchiga javob berish
    if found_domain or file_type:
        data = {
            "user": {
                "telegram_id": user.id,
                "username": user.username
            },
            "group": {
                "chat_id": chat.id,
                "title": chat.title
            },
            "message_id": message.message_id,
            "text": message_text if found_domain else "",
            "file_type": file_type
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(API_MESSAGE_URL, json=data) as resp:
                if resp.status == 201:
                    logging.info("Message saved successfully")

        # Foydalanuvchiga ogohlantirish xabari yuborish
        warning_message = "⚠️ Iltimos, bu faylni ochmang yoki ushbu havolaga kirmang! U xavfli bo'lishi mumkin."
        await message.reply(warning_message)  # <-- Foydalanuvchiga javob xabar yuborish
# Guruhga qo‘shilganda ishlovchi event
@dp.chat_member_handler()  # <--- BU YERDA @dp.chat_member() O'RNIGA @dp.chat_member_handler() ISHLATILDI
async def on_group_addition(update: ChatMemberUpdated):
    if update.new_chat_member.status in ["member", "administrator"]:
        chat = update.chat
        logging.info(f"Bot added to group: {chat.title}")

# Botni ishga tushirish
async def main():
    await dp.start_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())