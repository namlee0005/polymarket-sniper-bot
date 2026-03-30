import os

files = {
    "requirements.txt": """aiogram>=3.4.1
motor>=3.3.2
websockets>=12.0
httpx>=0.27.0
pydantic-settings>=2.2.1
python-dotenv>=1.0.1
""",
    "config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str = "placeholder"
    MONGODB_URI: str = "mongodb://mongo:27017/polymarket_sniper"
    POLYGONSCAN_API_KEY: str = ""
    X_BEARER_TOKEN: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
""",
    "database.py": """from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client.get_default_database()

bot_state_col = db.bot_state
tracked_events_col = db.tracked_events
keywords_col = db.keywords
whale_wallets_col = db.whale_wallets

async def init_db():
    state = await bot_state_col.find_one({"_id": "global"})
    if not state:
        await bot_state_col.insert_one({"_id": "global", "is_paused": False})

async def is_paused():
    state = await bot_state_col.find_one({"_id": "global"})
    return state and state.get("is_paused", False)

async def set_paused(paused: bool):
    await bot_state_col.update_one({"_id": "global"}, {"$set": {"is_paused": paused}}, upsert=True)
""",
    "main.py": """import asyncio
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
    await message.answer("Polymarket Sniper Bot Started! 🦈\\nCommands: /pause, /continue, /add_event")

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
""",
    "services/__init__.py": "",
    "services/gamma_poller.py": """import asyncio
import httpx
import logging
import database

async def fetch_top_events():
    # Fetch events > 500k vol, 10% volatility
    return []

async def start_poller(bot):
    logging.info("Starting Gamma Poller...")
    while True:
        if not await database.is_paused():
            events = await fetch_top_events()
            for event in events:
                # Format message and send via bot
                pass
        await asyncio.sleep(60)
""",
    "services/clob_listener.py": """import asyncio
import websockets
import json
import logging
import database
from services.wallet_profiler import analyze_wallet

async def start_clob_listener(bot):
    logging.info("Starting CLOB Listener...")
    uri = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    while True:
        try:
            async with websockets.connect(uri) as ws:
                while True:
                    msg = await ws.recv()
                    # Filter 'T' messages size > $10,000 (Ape In)
                    # Fetch tracked events and match condition_ids
                    # Trigger alert and analyze_wallet()
        except Exception as e:
            logging.error(f"CLOB WebSocket error: {e}")
            await asyncio.sleep(5)
""",
    "services/wallet_profiler.py": """import httpx
import logging

async def analyze_wallet(wallet_address: str) -> dict:
    \"\"\"
    Fetch Polymarket specific PnL, Win/Loss, and Txns from Gamma or Subgraph.
    \"\"\"
    logging.info(f"Analyzing wallet {wallet_address} via Polymarket Gamma/Subgraph...")
    return {
        "trades": 0,
        "win_rate": "0%",
        "profit": "$0",
        "loss": "$0"
    }
"""
}

for path, content in files.items():
    with open(path, "w") as f:
        f.write(content)

