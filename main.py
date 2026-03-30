import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import settings
import database
from services.gamma_poller import start_poller
from services.clob_listener import start_clob_listener

logging.basicConfig(level=logging.INFO)
bot = Bot(token=settings.TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Polymarket Sniper Bot Started! 🦈\nCommands: /pause, /continue, /add_event")

@dp.message(Command("pause"))
async def cmd_pause(message: types.Message):
    await database.set_paused(True)
    await message.answer("⏸ Bot paused. Alerts suspended.")

@dp.message(Command("continue"))
async def cmd_continue(message: types.Message):
    await database.set_paused(False)
    await message.answer("▶️ Bot continued. Alerts resumed.")

async def main():
    await database.init_db()
    
    # Start background tasks
    asyncio.create_task(start_poller(bot))
    asyncio.create_task(start_clob_listener(bot))
    
    # Start bot
    await dp.start_polling(bot)

if __name__ == "__main__":
    if settings.TELEGRAM_TOKEN == "placeholder":
        logging.error("Please set TELEGRAM_TOKEN in .env")
    else:
        asyncio.run(main())
