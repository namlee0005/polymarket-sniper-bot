# Polymarket Sniper Bot - Implementation Plan

## Phase 1: Project Setup & Telegram Bot Core
- [ ] Initialize Python 3.12+ project with `poetry` or `venv`
- [ ] Configure `requirements.txt` (`aiogram`, `motor`, `websockets`, `httpx`, `pydantic`, `python-dotenv`)
- [ ] Set up MongoDB Atlas connection via `motor`
- [ ] Create `config.py` for `.env` management (Telegram Bot Token, MongoDB URI, Polygonscan API Key, X API Key)
- [ ] Implement foundational `main.py` with `aiogram` Dispatcher
- [ ] Implement `bot_state` MongoDB collection
- [ ] Implement `/start`, `/pause`, and `/continue` commands

## Phase 2: Polymarket Gamma API & Volatility Tracker
- [ ] Create `services/gamma_poller.py` using `httpx` to poll Gamma API (`/events` and `/markets`)
- [ ] Implement logic to discover and save events with `volume > 500000` to MongoDB `tracked_events`
- [ ] Implement logic to compare `current_price` vs `last_price` and detect >= 10% change
- [ ] Implement `/add_event <url>` command: parse URL to find Event ID and manually insert to MongoDB
- [ ] Integrate Telegram notifier: send 📈 POLYMARKET ALERT message (formatting matched to spec) if `bot_state.is_paused` is False

## Phase 3: Polymarket CLOB WebSocket & Whale Tracker
- [ ] Create `services/clob_listener.py` using `websockets` to connect to Polymarket CLOB
- [ ] Subscribe CLOB listener to the `condition_ids` of all active `tracked_events`
- [ ] Implement parsing of Trade messages (`T`); filter for "Ape In" threshold (e.g., > $10,000 size)
- [ ] Create `services/polygonscan.py` to query maker's wallet address for transaction count (`tx_count`)
- [ ] Implement caching mechanism for wallet details to avoid Polygonscan rate limits
- [ ] Integrate Telegram notifier: send 🟢 BUY/🔴 SELL message with wallet Details & Tx link

## Phase 4: Keyword Tracking (Polymarket + X)
- [ ] Create `keywords` MongoDB collection
- [ ] Implement `/add_keyword <word>` and `/remove_keyword <word>` commands
- [ ] Update `gamma_poller.py` to check for keyword matches in new Polymarket events, regardless of volume
- [ ] Create `services/twitter_stream.py` to connect to X API
- [ ] Implement streaming or polling for X matching the stored keywords
- [ ] Integrate Telegram notifier for keyword alerts

## Phase 5: Hardening & Deployment
- [ ] Add robust error handling and reconnection logic for CLOB WebSocket
- [ ] Implement exponential backoff for Polygonscan and X API rate limits
- [ ] Create `Dockerfile` and `docker-compose.yml` for the bot
- [ ] Write `README.md` with setup instructions
- [ ] Deploy to VPS and test real-time alerts
