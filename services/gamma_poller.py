import asyncio
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
