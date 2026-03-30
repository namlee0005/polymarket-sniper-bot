# Polymarket Sniper Bot — Implementation Plan

## Phase 1: Foundation (Days 1–3)

### 1.1 Project Scaffold
- [x] Initialize repo: `requirements.txt` with `motor`, `aiogram`, `aiohttp`, `pydantic-settings`, `APScheduler` *(flat `polymarket/` layout; pyproject.toml not created — requirements.txt sufficient)*
- [ ] Configure `.env.example`: `TELEGRAM_TOKEN`, `MONGO_URI`, `POLYGONSCAN_API_KEY`, `TWITTER_BEARER_TOKEN`
- [x] Set up MongoDB connection via motor in `polymarket/database.py`; create indexes on `market_id`, `wallet`, `keyword`
- [x] Implement `polymarket/config.py` with pydantic-settings typed config class

### 1.2 Telegram Bot Shell
- [x] Create aiogram `Application` in `polymarket/main.py` with `/start`, `/pause`, `/resume` handlers
- [x] Implement pause/resume state: `/pause` and `/resume` commands writing to `bot_state` collection
- [x] Basic error handler and graceful shutdown hook (`finally` block disconnects MongoDB + closes bot session on exit)

---

## Phase 2: Polymarket Data Layer (Days 4–7)

### 2.1 Gamma API Poller
- [ ] Implement `src/poller/gamma.py`: fetch `/markets` with `volume_min=500000` filter, paginated
- [ ] Upsert results into `tracked_events`; log new markets discovered
- [ ] Schedule via APScheduler at 60s interval

### 2.2 CLOB WebSocket Listener
- [ ] Implement `src/poller/clob_ws.py`: connect to CLOB WS, subscribe to `trade` channel for tracked `market_id`s
- [ ] Parse trade messages; push `TradeEvent(market_id, price, size, side, timestamp)` to `asyncio.Queue`
- [ ] Auto-resubscribe when `tracked_events` collection changes (watch MongoDB change stream)

### 2.3 Manual Event Addition
- [ ] Implement `/add_event <url_or_slug>` handler: parse slug from URL, fetch market details from Gamma, insert with `source: manual`
- [ ] Validate market exists and meets no volume floor (manual = user override)

---

## Phase 3: Detectors (Days 8–11)

### 3.1 Volatility Detector
- [ ] Implement `src/detectors/volatility.py`: consume `TradeEvent` queue, maintain rolling price window (configurable, default 1h) per market
- [ ] Alert when `abs(current_price - window_open) / window_open >= 0.10`
- [ ] Debounce: suppress repeat alerts for same market within 30min cooldown
- [ ] Format alert: market name, current price, % change, volume, Polymarket link

### 3.2 Whale/Insider Tracker
- [ ] Implement `src/detectors/whale.py`: filter trades where `size >= whale_threshold` (default $5,000)
- [ ] Call `src/services/polygonscan.py` for wallet enrichment: portfolio size estimate (token holdings), tx count
- [ ] Cache results in `wallet_cache` with 24h TTL
- [ ] Format alert: wallet address (truncated), trade size/side, market, wallet stats, Polygonscan link

---

## Phase 4: Keyword Tracker (Days 12–14)

### 4.1 Polymarket Keyword Search
- [ ] Implement `src/poller/keywords.py`: poll Gamma `/markets?search=<keyword>` every 5min for each tracked keyword
- [ ] Deduplicate results against previously seen `market_id`s; alert on new matches

### 4.2 X/Twitter Keyword Monitor
- [ ] Implement `src/services/twitter.py`: connect to X API v2 filtered stream with keyword rules
- [ ] Fall back to recent search polling (15min) if stream access unavailable
- [ ] Alert format: tweet author, text preview, matched keyword, link

### 4.3 Keyword Management Commands
- [ ] `/add_keyword <keyword> [polymarket|twitter|both]` — insert into `keywords` collection for requesting `chat_id`
- [ ] `/remove_keyword <keyword>` — delete from collection
- [ ] `/list_keywords` — display active keywords with sources

---

## Phase 5: Notifier & Polish (Days 15–17)

### 5.1 Notifier
- [ ] Implement `src/notifier.py`: consume from alert queue, check `bot_state.paused` per `chat_id`, dispatch via aiogram bot
- [ ] Message templates for each alert type (volatility, whale, keyword); use Telegram MarkdownV2
- [ ] Rate-limit outbound messages to avoid Telegram flood limits (max 30/sec global, 1/sec per chat)

### 5.2 Additional Commands
- [ ] `/set_whale_threshold <amount>` — update per-chat threshold in `bot_state`
- [ ] `/tracked_events` — list currently monitored markets with volume and last price
- [ ] `/remove_event <slug>` — remove manually added event from tracking

### 5.3 Deployment
- [ ] Write `Dockerfile` (python:3.11-slim, non-root user)
- [ ] Write `docker-compose.yml` with `bot` + `mongo` services, volume for MongoDB data
- [ ] Add `healthcheck` endpoint (aiohttp minimal server) for container orchestration
- [ ] Document environment variables and deployment steps in `README.md`

---

## Milestones

| Milestone | Target | Definition of Done |
|---|---|---|
| M1: Bot Alive | Day 3 | `/start` responds, MongoDB connected, pause/resume works |
| M2: Market Data | Day 7 | Gamma poller running, CLOB WS connected, events in DB |
| M3: Alerts Live | Day 11 | Volatility + whale alerts delivered to Telegram |
| M4: Keywords | Day 14 | Keyword alerts from Polymarket + Twitter working |
| M5: Production | Day 17 | Dockerized, rate-limited, all commands implemented |