---
name: nanoquant-duckdb
description: >
  DuckDB storage skill for the NanoQuant trading agent. Use this skill whenever NanoQuant
  needs to store, query, or analyze trading data in DuckDB — including OHLCV bars from Alpaca,
  news/sentiment, Stockfit signals, or trade log entries. Triggers on: "store in duckdb",
  "save to database", "write to duckdb", "query the db", "load bars from db", "check trade log",
  "pull from duckdb", or any request to persist or retrieve NanoQuant pipeline data. This is
  step 3 (final step) of the NanoQuant pipeline — always run after nanoquant-alpaca and
  nanoquant-stockfit. Also use this skill standalone for any ad-hoc SQL queries against
  NanoQuant's trading database.
---

# NanoQuant — DuckDB Storage Skill

Persist and query all NanoQuant trading data using the `duckdb` MCP server. This is **step 3** (final step) of the pipeline. It also handles ad-hoc queries and analysis against stored data.

## MCP Server: `duckdb`

All tools below are called via the `duckdb` MCP server. The database file lives at `~/.openclaw/duckdb/trading.db` and persists across sessions.

---

## Tools

### `query`
Execute any SQL against DuckDB. The primary tool — use this for inserts, creates, selects, and everything else.

**Parameters:**
```
query       string    Required. Any valid DuckDB SQL statement.
session_id  string    Optional. Pass a session ID to track query history across calls.
```

**Returns:** Query results as a JSON string. For INSERT/CREATE statements, returns a confirmation.

**Important:** DuckDB is an analytical database. It supports full SQL including window functions, CTEs, UNNEST, LIST, STRUCT, JSON extraction, and direct file querying (`read_csv`, `read_parquet`, `read_json`).

---

### `analyze_schema`
Inspect the schema of a file or table without running a full query.

**Parameters:**
```
file_path   string    Required. Local file path or S3 URL. e.g. "~/data/bars.parquet" or "s3://bucket/file.parquet"
session_id  string    Optional.
```

**Returns:** Column names, types, and sample values.

---

### `analyze_data`
Run statistical profiling on a table or file (min, max, mean, nulls, cardinality per column).

**Parameters:**
```
file_path   string    Required. Table name or file path. e.g. "ohlcv_bars" or "~/data/bars.csv"
session_id  string    Optional.
```

**Returns:** Statistical summary per column.

---

### `create_session`
Create or reset a session for context tracking across multiple `query` calls.

**Parameters:**
```
session_id  string    Optional. Provide to reset an existing session; omit to create a new one.
```

**Returns:** `{ "session_id": "..." }`

Start each pipeline run with `create_session` and pass the returned ID to all subsequent `query` calls.

---

### `suggest_visualizations`
Get visualization recommendations for a table or file.

**Parameters:**
```
file_path   string    Required. Table name or file path.
session_id  string    Optional.
```

**Returns:** Suggested chart types and the SQL to generate them.

---

## NanoQuant Table Schemas

Run these CREATE statements once to initialize the database. They are idempotent (`IF NOT EXISTS`).

### `ohlcv_bars` — Price/volume history
```sql
CREATE TABLE IF NOT EXISTS ohlcv_bars (
    symbol      VARCHAR NOT NULL,
    timeframe   VARCHAR NOT NULL,           -- "1Min", "1Day", etc.
    ts          TIMESTAMPTZ NOT NULL,       -- bar timestamp
    open        DOUBLE,
    high        DOUBLE,
    low         DOUBLE,
    close       DOUBLE,
    volume      BIGINT,
    vwap        DOUBLE,                     -- volume-weighted avg price
    trade_count INTEGER,                    -- number of trades (field "n" from Alpaca)
    inserted_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (symbol, timeframe, ts)
);
```

### `news_sentiment` — News articles per symbol
```sql
CREATE TABLE IF NOT EXISTS news_sentiment (
    id          BIGINT PRIMARY KEY,         -- Alpaca news article ID
    symbol      VARCHAR NOT NULL,
    headline    VARCHAR,
    summary     TEXT,
    content     TEXT,
    author      VARCHAR,
    source      VARCHAR,
    url         VARCHAR,
    published_at TIMESTAMPTZ,
    inserted_at  TIMESTAMPTZ DEFAULT now()
);
```

### `stockfit_signals` — Screener and signal results
```sql
CREATE TABLE IF NOT EXISTS stockfit_signals (
    id          VARCHAR DEFAULT gen_random_uuid()::VARCHAR,
    symbol      VARCHAR NOT NULL,
    signal_date DATE NOT NULL,
    signal_type VARCHAR,                    -- e.g. "breakout", "momentum", "screener"
    direction   VARCHAR,                    -- "long", "short", "neutral"
    strength    DOUBLE,                     -- signal strength score (0–1 or tool-specific)
    timeframe   VARCHAR,                    -- "1D", "1W", "intraday"
    raw_data    JSON,                       -- full response object from Stockfit, unmodified
    inserted_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (symbol, signal_date, signal_type)
);
```

### `trade_log` — Executed or simulated trades
```sql
CREATE TABLE IF NOT EXISTS trade_log (
    id           VARCHAR DEFAULT gen_random_uuid()::VARCHAR PRIMARY KEY,
    symbol       VARCHAR NOT NULL,
    side         VARCHAR NOT NULL,          -- "long" or "short"
    entry_price  DOUBLE,
    exit_price   DOUBLE,
    qty          DOUBLE,
    entry_at     TIMESTAMPTZ,
    exit_at      TIMESTAMPTZ,
    pnl          DOUBLE,                    -- realized P&L in dollars
    pnl_pct      DOUBLE,                    -- P&L as percentage
    strategy     VARCHAR,                   -- e.g. "ORB", "VWAP", "momentum"
    notes        TEXT,
    inserted_at  TIMESTAMPTZ DEFAULT now()
);
```

---

## Storing Pipeline Data

### Insert Alpaca bars
Map Alpaca's response fields (`t`, `o`, `h`, `l`, `c`, `v`, `vw`, `n`) to the `ohlcv_bars` columns:

```sql
INSERT OR IGNORE INTO ohlcv_bars (symbol, timeframe, ts, open, high, low, close, volume, vwap, trade_count)
VALUES
  ('SPY', '1Day', '2025-01-02T00:00:00Z', 592.10, 595.40, 589.80, 594.20, 85200000, 592.87, 1240512),
  -- repeat for each bar
;
```

Use `INSERT OR IGNORE` to skip duplicates — the primary key on `(symbol, timeframe, ts)` prevents double-inserts on re-runs.

### Insert Alpaca news
Map from Alpaca's news array. A single article may cover multiple symbols — insert one row per symbol:

```sql
INSERT OR IGNORE INTO news_sentiment (id, symbol, headline, summary, content, author, source, url, published_at)
VALUES (12345, 'SPY', 'Fed holds rates steady...', '...', '...', 'John Smith', 'Benzinga', 'https://...', '2025-01-15T10:30:00Z');
```

### Insert Stockfit signals
Store the full raw JSON response alongside the parsed fields so nothing is lost:

```sql
INSERT OR REPLACE INTO stockfit_signals (symbol, signal_date, signal_type, direction, strength, timeframe, raw_data)
VALUES ('MES', '2025-05-01', 'momentum', 'long', 0.82, '1D', '{"score": 0.82, "rsi": 58, "adx": 32}');
```

---

## Common Queries

**Latest bars for a symbol:**
```sql
SELECT * FROM ohlcv_bars
WHERE symbol = 'SPY' AND timeframe = '1Day'
ORDER BY ts DESC LIMIT 30;
```

**Recent signals:**
```sql
SELECT symbol, signal_date, signal_type, direction, strength
FROM stockfit_signals
WHERE signal_date >= current_date - INTERVAL '7 days'
ORDER BY signal_date DESC, strength DESC;
```

**News for a symbol this week:**
```sql
SELECT headline, published_at, source
FROM news_sentiment
WHERE symbol = 'SPY' AND published_at >= current_date - INTERVAL '7 days'
ORDER BY published_at DESC;
```

**Trade log P&L summary:**
```sql
SELECT strategy, COUNT(*) AS trades,
       SUM(pnl) AS total_pnl,
       AVG(pnl_pct) AS avg_pnl_pct,
       SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS win_rate
FROM trade_log
GROUP BY strategy ORDER BY total_pnl DESC;
```

---

## Pipeline Pattern

This skill is **step 3** (final step) of the NanoQuant data pipeline:

```
[nanoquant-alpaca]   → fetch bars + news         (step 1)
[nanoquant-stockfit] → fetch signals              (step 2)
[nanoquant-duckdb]   → store everything           (step 3) ← YOU ARE HERE
```

**Standard pipeline run:**
1. `create_session` → get a `session_id`
2. Run `query` with the `ohlcv_bars` CREATE TABLE (if first run)
3. Run `query` to INSERT bars from Alpaca
4. Run `query` to INSERT news from Alpaca
5. Run `query` to INSERT signals from Stockfit
6. Confirm row counts with `SELECT COUNT(*) FROM ohlcv_bars WHERE inserted_at > now() - INTERVAL '1 minute'`

## Utility Scripts

Two scripts bypass the MCP for heavy operations — use them when inserting large datasets (months of 1-minute bars, bulk news loads) that would be slow through MCP one-call-at-a-time.

### `init_db.py` — Create all 4 tables
```bash
# Initialize with default DB path (~/.openclaw/duckdb/trading.db)
python skills/trading_skills/nanoquant-duckdb/scripts/init_db.py

# Custom DB path
python init_db.py --db ~/custom/nanoquant.db

# Verify existing schema + row counts without creating anything
python init_db.py --verify
```

### `bulk_insert.py` — Insert rows from normalized JSON
```bash
# Insert pre-normalized bars rows
python skills/trading_skills/nanoquant-duckdb/scripts/bulk_insert.py \
  --table ohlcv_bars --input bars_rows.json

# Full pipeline: fetch → normalize → insert
python normalize_alpaca.py bars --input raw_alpaca.json --timeframe 1Day \
  | python bulk_insert.py --table ohlcv_bars

# Dry run to validate rows before committing
python bulk_insert.py --table ohlcv_bars --input bars.json --dry-run
```

Supports all 4 tables: `ohlcv_bars`, `news_sentiment`, `stockfit_signals`, `trade_log`.

## Initialization (first-time setup)
Run this once to create all tables:

```sql
CREATE TABLE IF NOT EXISTS ohlcv_bars ( ... );
CREATE TABLE IF NOT EXISTS news_sentiment ( ... );
CREATE TABLE IF NOT EXISTS stockfit_signals ( ... );
CREATE TABLE IF NOT EXISTS trade_log ( ... );
```

Or ask NanoQuant: *"Initialize the DuckDB trading database"* — this skill will run all four CREATE statements.
