from motor.motor_asyncio import AsyncIOMotorClient
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
