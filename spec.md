# Polymarket Sniper Bot - Architecture Specification

## 1. Executive Summary
A high-performance, asynchronous Telegram bot designed to monitor Polymarket for significant price volatility, track large insider/whale trades ("ape in"), and alert on specific keywords across both Polymarket and X (Twitter). The bot uses a persistent MongoDB database to manage tracked events, keywords, and global pause/resume state.

## 2. Core Features & Requirements

### 2.1. Price Volatility Tracker
- **Target:** Crypto and World events with >$500k volume.
- **Trigger:** Price change of >=10% (up or down).
- **Manual Addition:** Users can explicitly add specific events via Telegram command.
- **Alert Output:** Includes Event Name, Specific Market/Outcome, % Change, Current/Previous Price, Total Volume, and URL.

### 2.2. Insider / Whale Tracker
- **Target:** Monitors the CLOB (Central Limit Order Book) for large executions.
- **Enrichment:** On detecting a large trade, the bot extracts the maker's wallet address and queries Polygonscan.
- **Alert Output:** Includes Size, Price, Previous Transactions count, and a direct Polygonscan TX link.

### 2.3. Keyword Tracker
- **Polymarket:** Scans new and existing markets for user-defined keywords (e.g., "Trump", "BTC").
- **Twitter (X):** Monitors tweets matching the keywords (requires X API integration).
- **Control:** Users can add/remove keywords dynamically.

### 2.4. Bot Control Commands
- `/add_event <url_or_id>`: Manually force the bot to track a specific Polymarket event.
- `/add_keyword <word>`: Add a keyword to the monitoring list.
- `/pause`: Suspends all outbound alerts.
- `/continue` (or `/resume`): Restores outbound alerts.

## 3. Architecture & Tech Stack

**Language:** Python 3.12+ (Asyncio)
This ensures the bot can handle high-frequency WebSocket connections (CLOB) and HTTP polling concurrently without blocking the Telegram interface.

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Telegram Framework** | `aiogram` | Fully asynchronous, robust Telegram bot API wrapper. |
| **Database** | MongoDB (`motor`) | Async MongoDB driver for storing tracked events, state, and wallet cache. |
| **Polymarket APIs** | `websockets`, `httpx` | Gamma API (REST) for market discovery/volume; CLOB API (WS) for real-time trades. |
| **Blockchain Explorer** | `httpx` (Polygonscan API) | Fetching wallet transaction counts and histories. |
| **Twitter/X API** | `tweepy` or `httpx` | Streaming or polling for keyword mentions. |

## 4. Database Schema (MongoDB)

- **`bot_state`**:
  - `_id`: "global"
  - `is_paused`: boolean
- **`tracked_events`**:
  - `event_id`: string (Primary Key)
  - `title`: string
  - `volume`: number
  - `last_price`: number (for volatility calculation)
  - `is_manual`: boolean
- **`keywords`**:
  - `word`: string (Primary Key)
  - `added_by`: string
- **`whale_wallets`**:
  - `address`: string (Primary Key)
  - `tx_count`: number (Cached to avoid spamming Polygonscan)

## 5. Event Loop Design
1. **Gamma Poller (Every 60s):** Fetches top events by volume. Adds new events >$500k to `tracked_events`. Checks for 10% price delta.
2. **CLOB Listener (Continuous):** WebSocket connection subscribed to all `tracked_events` condition IDs. Triggers on large `T` (Trade) messages.
3. **Telegram Dispatcher:** Listens for commands (`/pause`, `/add_event`). Checks `bot_state.is_paused` before sending any alert from the Poller or Listener.
