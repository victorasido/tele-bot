# bot.py
import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties  # ⬅️ import baru

from handlers import menu, hero, counter, gameplay, comp, tierlist

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN kosong. Isi di .env")

print("[BOOT] Telegram token OK")
print("[BOOT] Gemini:", "AKTIF" if GEMINI_API_KEY else "TIDAK ADA (pakai dummy)")

# ⬇️ gunakan DefaultBotProperties, bukan parse_mode= di Bot()
bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

# Registrasi router

dp.include_router(menu.router)  
dp.include_router(hero.router)
dp.include_router(counter.router)
dp.include_router(gameplay.router)
dp.include_router(comp.router)
dp.include_router(tierlist.router)

async def main():
    me = await bot.get_me()
    print(f"[BOOT] @{me.username} ready")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
