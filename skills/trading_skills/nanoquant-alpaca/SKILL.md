---
name: nanoquant-alpaca
description: >
  Alpaca MCP data fetching for the NanoQuant trading agent. Use this skill whenever NanoQuant
  needs to fetch OHLCV price bars, news articles, tradable assets, or the market trading
  calendar from Alpaca. Triggers on: "get bars for", "fetch price history", "pull OHLCV",
  "get news for", "what's tradable", "market calendar", "trading days", or any request
  to retrieve Alpaca market data before storing it. Always use this skill before the
  nanoquant-duckdb skill when building a data pipeline — Alpaca is step 1.
---

# NanoQuant — Alpaca MCP Skill

Fetch market data from Alpaca via the `alpaca-mcp` MCP server. This is **step 1** of the NanoQuant pipeline. After fetching, hand off to the `nanoquant-duckdb` skill to store results.

## MCP Server: `alpaca-mcp`

All tools below are called via the `alpaca-mcp` MCP server. The server authenticates automatically using the `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` set in OpenClaw config.

---

## Tools

### `get-stock-bars`
Fetch OHLCV (Open/High/Low/Close/Volume) bars for one or more symbols.

**Parameters:**
```
symbols    string[]   Required. Array of ticker symbols. e.g. ["MES", "ES", "SPY", "QQQ"]
start      string     Required. ISO 8601 start datetime. e.g. "2025-01-01T00:00:00Z"
end        string     Required. ISO 8601 end datetime.   e.g. "2025-12-31T23:59:59Z"
timeframe  string     Required. Bar resolution.
                      Common values: "1Min", "5Min", "15Min", "30Min", "1Hour", "4Hour", "1Day", "1Week"
```

**Returns:** `{ "bars": { "SPY": [ { "t": "...", "o": 0.0, "h": 0.0, "l": 0.0, "c": 0.0, "v": 0, "vw": 0.0, "n": 0 }, ... ] } }`

Each bar object fields:
- `t` — timestamp (ISO 8601)
- `o` — open price
- `h` — high price
- `l` — low price
- `c` — close price
- `v` — volume
- `vw` — volume-weighted average price
- `n` — number of trades

**Note:** Pagination is handled automatically. Large date ranges or many symbols are batched internally (2000 symbols per batch).

**Example usage:**
```
Fetch daily bars for MES and ES from Jan 1 2025 to today
→ get-stock-bars({ symbols: ["MES", "ES"], start: "2025-01-01T00:00:00Z", end: "2025-05-01T00:00:00Z", timeframe: "1Day" })
```

---

### `get-news`
Fetch news articles for one or more symbols, with full article content.

**Parameters:**
```
symbols    string[]   Required. Array of ticker symbols. e.g. ["SPY", "QQQ"]
start      string     Required. ISO 8601 start date. e.g. "2025-01-01T00:00:00Z"
end        string     Required. ISO 8601 end date.   e.g. "2025-05-01T00:00:00Z"
```

**Returns:** Array of news article objects:
```json
[
  {
    "id": 12345,
    "headline": "...",
    "summary": "...",
    "content": "...",
    "author": "...",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "...",
    "url": "https://...",
    "symbols": ["SPY"],
    "source": "Benzinga"
  }
]
```

**Note:** Returns articles in descending order (newest first). Full article content is included (`include_content: true`). Pagination handled automatically.

---

### `get-market-days`
Fetch the Alpaca trading calendar — which days markets were/are open and their open/close times.

**Parameters:**
```
start    string   Required. Date string. e.g. "2025-01-01"
end      string   Required. Date string. e.g. "2025-12-31"
```

**Returns:** Array of market day objects:
```json
[
  {
    "date": "2025-01-02",
    "open": "09:30",
    "close": "16:00",
    "session_open": "04:00",
    "session_close": "20:00"
  }
]
```

Use this before fetching bars to avoid requesting data for weekends/holidays.

---

### `get-assets`
List all currently tradable assets on Alpaca.

**Parameters:**
```
assetClass    string   Optional. "us_equity" (default) or "crypto"
```

**Returns:** Array of tradable asset objects with fields like `symbol`, `name`, `exchange`, `asset_class`, `status`, `tradable`, `marginable`, `shortable`, `fractionable`.

Use this to validate symbols before calling `get-stock-bars`.

---

## Pipeline Pattern

This skill is **step 1** of the NanoQuant data pipeline:

```
[nanoquant-alpaca] → fetch bars + news
         ↓
[nanoquant-stockfit] → fetch signals for same symbols
         ↓
[nanoquant-duckdb] → store all results
```

After fetching from Alpaca, pass the raw data objects directly to the `nanoquant-duckdb` skill's storage functions. Do not transform the data — the DuckDB skill handles schema mapping.

## Common Workflows

**Pre-market data pull:**
1. Call `get-market-days` to confirm today is a trading day
2. Call `get-stock-bars` for watchlist symbols, timeframe `"1Day"`, last 30–90 days
3. Call `get-news` for same symbols, last 7 days
4. Hand off to `nanoquant-duckdb` to store

**Backtest data pull:**
1. Call `get-stock-bars` for target symbols over full backtest window
2. Store in DuckDB `ohlcv_bars` table via `nanoquant-duckdb`

**Error handling:**
If any tool returns `isError: true`, log the error text and retry once before failing. Rate limits are handled internally by the MCP server.

## Utility Script

Use `normalize_alpaca.py` to remap raw Alpaca MCP responses to DuckDB-ready rows. Handles field renaming (`t→ts`, `o→open`, `vw→vwap`, `n→trade_count`) and per-symbol expansion for news.

```bash
# Normalize bars → JSON rows
python skills/trading_skills/nanoquant-alpaca/scripts/normalize_alpaca.py \
  bars --input raw_bars.json --timeframe 1Day

# Pipe directly into bulk_insert
python normalize_alpaca.py bars --input raw_bars.json --timeframe 1Day \
  | python skills/trading_skills/nanoquant-duckdb/scripts/bulk_insert.py --table ohlcv_bars

# Output as SQL INSERT statements
python normalize_alpaca.py bars --input raw_bars.json --timeframe 1Day --format sql

# Normalize news articles
python normalize_alpaca.py news --input raw_news.json
```
