import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Import Handler
from handlers import menu, hero, comp, counter, gameplay, tierlist

# Import Inisiator Worker Gemini
from core.gemini import init_gemini_worker  # <--- TAMBAHAN 1

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def main():
    logging.basicConfig(level=logging.INFO)
    
    if not TOKEN:
        print("Error: BOT_TOKEN tidak ditemukan di .env")
        return

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Register Router
    dp.include_router(menu.router)
    dp.include_router(hero.router)
    dp.include_router(comp.router)
    dp.include_router(counter.router)
    dp.include_router(gameplay.router)
    dp.include_router(tierlist.router)

    # Delete webhook biar gak conflict
    await bot.delete_webhook(drop_pending_updates=True)
    
    # --- NYALAKAN MESIN ANTRIAN ---
    await init_gemini_worker()  # <--- TAMBAHAN 2 (PENTING!)
    
    print("🤖 @Dapsssbot Berjalan dengan Sistem Antrian...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot dimatikan.")