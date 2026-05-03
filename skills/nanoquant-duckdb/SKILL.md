---
name: nanoquant-duckdb
description: >
  DuckDB storage skill for the NanoQuant trading agent. Use this skill whenever NanoQuant
  needs to store, query, or analyze trading data in DuckDB — including OHLCV bars from Alpaca,
  news/sentiment, Stockfit signals, trade log entries, account equity snapshots, or
  strategy performance stats. Triggers on: "store in duckdb", "save to database",
  "write to duckdb", "query the db", "load bars from db", "check trade log", "account
  snapshot", "strategy performance", "pull from duckdb", "goal progress", "win rate".
  This is step 3 (final step) of the NanoQuant data pipeline — always run after
  nanoquant-alpaca and nanoquant-stockfit. Also use standalone for any ad-hoc queries.
---

# NanoQuant — DuckDB Storage Skill

Persist and query all NanoQuant trading data using the `duckdb` MCP server. This is
**step 3** of the data pipeline, and the shared state layer for all four managers.

## MCP Server: `duckdb`

All tools are called via the `duckdb` MCP server. The database file lives at
`~/.openclaw/duckdb/trading.db` and persists across sessions.

---

## Tools

### `query`
Execute any SQL against DuckDB. The primary tool — use for inserts, creates, selects, everything.

**Parameters:**
```
query       string    Required. Any valid DuckDB SQL statement.
session_id  string    Optional. Pass a session ID to track query history across calls.
```

**Returns:** Query results as JSON. For INSERT/CREATE, returns a confirmation.

---

### `analyze_schema`
Inspect the schema of a file or table.

**Parameters:**
```
file_path   string    Required. Table name or file path.
session_id  string    Optional.
```

---

### `analyze_data`
Statistical profiling on a table (min, max, mean, nulls, cardinality).

**Parameters:**
```
file_path   string    Required. Table name or file path.
session_id  string    Optional.
```

---

### `create_session`
Create or reset a session for context tracking across multiple `query` calls.

**Parameters:**
```
session_id  string    Optional.
```

**Returns:** `{ "session_id": "..." }`

Start each pipeline run with `create_session` and pass the ID to all subsequent calls.

---

## Full Database Schema

Run `initialize_database` (see below) once on first setup. All statements are idempotent.

---

### `ohlcv_bars` — Price / volume history (existing)
```sql
CREATE TABLE IF NOT EXISTS ohlcv_bars (
    symbol      VARCHAR NOT NULL,
    timeframe   VARCHAR NOT NULL,
    ts          TIMESTAMPTZ NOT NULL,
    open        DOUBLE,
    high        DOUBLE,
    low         DOUBLE,
    close       DOUBLE,
    volume      BIGINT,
    vwap        DOUBLE,
    trade_count INTEGER,
    inserted_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (symbol, timeframe, ts)
);
```

---

### `news_sentiment` — News articles per symbol (existing)
```sql
CREATE TABLE IF NOT EXISTS news_sentiment (
    id           BIGINT PRIMARY KEY,
    symbol       VARCHAR NOT NULL,
    headline     VARCHAR,
    summary      TEXT,
    content      TEXT,
    author       VARCHAR,
    source       VARCHAR,
    url          VARCHAR,
    published_at TIMESTAMPTZ,
    inserted_at  TIMESTAMPTZ DEFAULT now()
);
```

---

### `stockfit_signals` — Screener and signal results (existing)
```sql
CREATE TABLE IF NOT EXISTS stockfit_signals (
    id          VARCHAR DEFAULT gen_random_uuid()::VARCHAR,
    symbol      VARCHAR NOT NULL,
    signal_date DATE NOT NULL,
    signal_type VARCHAR,
    direction   VARCHAR,
    strength    DOUBLE,
    timeframe   VARCHAR,
    raw_data    JSON,
    inserted_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (symbol, signal_date, signal_type)
);
```

---

### `trade_log` — All paper trades (existing + extended)
```sql
CREATE TABLE IF NOT EXISTS trade_log (
    id            VARCHAR DEFAULT gen_random_uuid()::VARCHAR PRIMARY KEY,
    symbol        VARCHAR NOT NULL,
    side          VARCHAR NOT NULL,       -- "long" or "short"
    entry_price   DOUBLE,
    exit_price    DOUBLE,
    qty           DOUBLE,
    entry_at      TIMESTAMPTZ,
    exit_at       TIMESTAMPTZ,
    pnl           DOUBLE,                -- realized P&L in dollars
    pnl_pct       DOUBLE,                -- P&L as percentage
    strategy      VARCHAR,               -- e.g. "ORB_1D", "VWAP_MOM"
    strategy_tag  VARCHAR,               -- same as strategy, for filtering
    is_paper      BOOLEAN DEFAULT TRUE,  -- ALWAYS true until graduation
    notes         TEXT,                  -- order ID, rejection reason, etc.
    inserted_at   TIMESTAMPTZ DEFAULT now()
);

-- Run these if upgrading from the original schema:
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS strategy_tag VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS is_paper BOOLEAN DEFAULT TRUE;
```

**strategy values:** `ORB_1D` (Opening Range Breakout), `VWAP_MOM` (VWAP Momentum),
`GAP_FADE`, `BREAKOUT`, `MEAN_REV` — add new ones as strategies are developed.

---

### `account_snapshots` — Daily equity curve 🆕
```sql
CREATE TABLE IF NOT EXISTS account_snapshots (
    snapshot_date       DATE NOT NULL PRIMARY KEY,
    equity              DOUBLE NOT NULL,     -- total account value (cash + positions)
    cash                DOUBLE,              -- settled cash
    positions_value     DOUBLE,              -- market value of open positions
    daily_pnl           DOUBLE,              -- equity - last_equity (from Alpaca)
    daily_return_pct    DOUBLE,              -- daily_pnl / prior_equity
    cumul_return_pct    DOUBLE,              -- (equity - 100000) / 100000
    goal_progress_pct   DOUBLE,              -- equity / 1000000 (toward $1M)
    open_positions      INTEGER,             -- count of open positions at close
    trades_today        INTEGER,             -- number of fills today
    inserted_at         TIMESTAMPTZ DEFAULT now()
);
```

**Source:** analytics_manager pulls from Alpaca `get-account` + `get-portfolio-history`
at EOD and writes one row per trading day. Starting equity is $100,000.

---

### `strategy_performance` — Per-strategy rolling stats 🆕
```sql
CREATE TABLE IF NOT EXISTS strategy_performance (
    strategy          VARCHAR NOT NULL,
    eval_date         DATE NOT NULL,
    total_trades      INTEGER DEFAULT 0,
    winning_trades    INTEGER DEFAULT 0,
    win_rate          DOUBLE,               -- winning_trades / total_trades
    total_pnl         DOUBLE,               -- sum of all closed pnl
    avg_pnl_per_trade DOUBLE,               -- total_pnl / total_trades
    avg_return_pct    DOUBLE,               -- avg pnl_pct across trades
    best_trade_pnl    DOUBLE,
    worst_trade_pnl   DOUBLE,
    sharpe_ratio      DOUBLE,               -- annualized: avg_ret / stddev_ret * sqrt(252)
    max_drawdown      DOUBLE,               -- max peak-to-trough drop in pnl
    avg_holding_hours DOUBLE,               -- avg (exit_at - entry_at) in hours
    is_active         BOOLEAN DEFAULT TRUE, -- still being traded
    grad_ready        BOOLEAN DEFAULT FALSE,-- meets criteria to go live
    grad_note         TEXT,                 -- why it is/isn't ready
    PRIMARY KEY (strategy, eval_date)
);
```

**Graduation criteria (analytics_manager evaluates weekly after 30+ trades):**
- `win_rate >= 0.55` (55% win rate)
- `sharpe_ratio >= 1.5`
- `max_drawdown <= 0.15` (max 15% drawdown on strategy capital)
- `total_trades >= 30` (sufficient sample size)

When all four criteria are met, set `grad_ready = TRUE` and notify Tyler for review.

---

## Initialization (run once on first setup)

```sql
-- Step 1: Core tables
CREATE TABLE IF NOT EXISTS ohlcv_bars ( ... );         -- see schema above
CREATE TABLE IF NOT EXISTS news_sentiment ( ... );
CREATE TABLE IF NOT EXISTS stockfit_signals ( ... );
CREATE TABLE IF NOT EXISTS trade_log ( ... );
CREATE TABLE IF NOT EXISTS account_snapshots ( ... );
CREATE TABLE IF NOT EXISTS strategy_performance ( ... );

-- Step 2: Upgrade existing trade_log if needed
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS strategy_tag VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS is_paper BOOLEAN DEFAULT TRUE;

-- Step 3: Seed starting state
INSERT OR IGNORE INTO account_snapshots (
    snapshot_date, equity, cash, positions_value,
    daily_pnl, daily_return_pct, cumul_return_pct, goal_progress_pct,
    open_positions, trades_today
) VALUES (
    current_date, 100000.00, 100000.00, 0.00,
    0.00, 0.00, 0.00, 0.10,
    0, 0
);
```

---

## Storing Pipeline Data

### Insert Alpaca OHLCV bars
```sql
INSERT OR IGNORE INTO ohlcv_bars
    (symbol, timeframe, ts, open, high, low, close, volume, vwap, trade_count)
VALUES
    ('SPY', '1Day', '2026-05-01T00:00:00Z', 592.10, 595.40, 589.80, 594.20,
     85200000, 592.87, 1240512);
```

### Insert Alpaca news
```sql
INSERT OR IGNORE INTO news_sentiment
    (id, symbol, headline, summary, content, author, source, url, published_at)
VALUES
    (12345, 'SPY', 'Fed holds rates steady', '...', '...', 'John Smith',
     'Benzinga', 'https://...', '2026-05-01T10:30:00Z');
```

### Insert Stockfit signals
```sql
INSERT OR REPLACE INTO stockfit_signals
    (symbol, signal_date, signal_type, direction, strength, timeframe, raw_data)
VALUES
    ('QQQ', '2026-05-01', 'breakout', 'long', 0.87, '1D',
     '{"score": 0.87, "rsi": 62, "adx": 35}');
```

### Write a paper trade entry
```sql
INSERT INTO trade_log (
    symbol, side, entry_price, qty, entry_at,
    strategy, strategy_tag, is_paper, notes
) VALUES (
    'QQQ', 'long', 442.30, 22,
    '2026-05-01T09:31:05Z',
    'ORB_1D', 'ORB_1D', TRUE,
    'client_order_id: clawx-ORB_1D-20260501-QQQ'
);
```

### Write a paper trade exit
```sql
UPDATE trade_log
SET exit_price  = 445.80,
    exit_at     = '2026-05-01T14:22:10Z',
    pnl         = (445.80 - 442.30) * 22,
    pnl_pct     = (445.80 - 442.30) / 442.30
WHERE symbol       = 'QQQ'
  AND strategy_tag = 'ORB_1D'
  AND exit_at IS NULL
  AND entry_at     = '2026-05-01T09:31:05Z';
```

### Write EOD account snapshot
```sql
INSERT OR REPLACE INTO account_snapshots (
    snapshot_date, equity, cash, positions_value,
    daily_pnl, daily_return_pct, cumul_return_pct, goal_progress_pct,
    open_positions, trades_today
) VALUES (
    '2026-05-01',
    100842.50,
    85000.00,
    15842.50,
    842.50,
    0.008425,
    0.008425,               -- (100842.50 - 100000) / 100000
    0.100843,               -- 100842.50 / 1000000
    3,
    5
);
```

### Update strategy performance (run weekly)
```sql
INSERT OR REPLACE INTO strategy_performance (
    strategy, eval_date, total_trades, winning_trades, win_rate,
    total_pnl, avg_pnl_per_trade, avg_return_pct,
    best_trade_pnl, worst_trade_pnl,
    sharpe_ratio, max_drawdown, avg_holding_hours,
    is_active, grad_ready, grad_note
)
SELECT
    strategy,
    current_date                                                   AS eval_date,
    COUNT(*)                                                       AS total_trades,
    COUNT(*) FILTER (WHERE pnl > 0)                                AS winning_trades,
    COUNT(*) FILTER (WHERE pnl > 0)::DOUBLE / COUNT(*)            AS win_rate,
    SUM(pnl)                                                       AS total_pnl,
    AVG(pnl)                                                       AS avg_pnl_per_trade,
    AVG(pnl_pct)                                                   AS avg_return_pct,
    MAX(pnl)                                                       AS best_trade_pnl,
    MIN(pnl)                                                       AS worst_trade_pnl,
    AVG(pnl_pct) / NULLIF(STDDEV(pnl_pct), 0) * SQRT(252)        AS sharpe_ratio,
    MIN(pnl)                                                       AS max_drawdown,
    AVG(EPOCH(exit_at - entry_at) / 3600.0)                       AS avg_holding_hours,
    TRUE                                                           AS is_active,
    (COUNT(*) >= 30
     AND COUNT(*) FILTER (WHERE pnl > 0)::DOUBLE / COUNT(*) >= 0.55
     AND AVG(pnl_pct) / NULLIF(STDDEV(pnl_pct), 0) * SQRT(252) >= 1.5
     AND MIN(pnl) >= -0.15 * AVG(entry_price * qty)
    )                                                              AS grad_ready,
    CASE
        WHEN COUNT(*) < 30
            THEN 'Insufficient trades (' || COUNT(*) || '/30)'
        WHEN COUNT(*) FILTER (WHERE pnl > 0)::DOUBLE / COUNT(*) < 0.55
            THEN 'Win rate too low: ' || ROUND(COUNT(*) FILTER (WHERE pnl > 0)::DOUBLE / COUNT(*) * 100, 1) || '%'
        WHEN AVG(pnl_pct) / NULLIF(STDDEV(pnl_pct), 0) * SQRT(252) < 1.5
            THEN 'Sharpe too low: ' || ROUND(AVG(pnl_pct) / NULLIF(STDDEV(pnl_pct), 0) * SQRT(252), 2)
        ELSE 'Meets all graduation criteria'
    END                                                            AS grad_note
FROM trade_log
WHERE is_paper = TRUE
  AND exit_at IS NOT NULL
  AND strategy IS NOT NULL
GROUP BY strategy;
```

---

## Key Analytics Queries

### Today's P&L
```sql
SELECT
    snapshot_date,
    equity,
    daily_pnl,
    ROUND(daily_return_pct * 100, 3) || '%'      AS daily_return,
    ROUND(cumul_return_pct * 100, 2) || '%'      AS total_return,
    ROUND(goal_progress_pct * 100, 2) || '%'     AS progress_to_1M
FROM account_snapshots
ORDER BY snapshot_date DESC
LIMIT 7;
```

### Equity curve (all time)
```sql
SELECT snapshot_date, equity, cumul_return_pct
FROM account_snapshots
ORDER BY snapshot_date ASC;
```

### Strategy leaderboard
```sql
SELECT
    strategy,
    total_trades,
    ROUND(win_rate * 100, 1) || '%'     AS win_rate,
    ROUND(total_pnl, 2)                 AS total_pnl,
    ROUND(sharpe_ratio, 2)              AS sharpe,
    grad_ready,
    grad_note
FROM strategy_performance
WHERE eval_date = (SELECT MAX(eval_date) FROM strategy_performance)
ORDER BY total_pnl DESC;
```

### Open trades (unrealized P&L needs Alpaca for current price)
```sql
SELECT symbol, side, entry_price, qty, entry_at, strategy_tag
FROM trade_log
WHERE exit_at IS NULL
  AND is_paper = TRUE
ORDER BY entry_at DESC;
```

### Best and worst trades
```sql
SELECT symbol, strategy, entry_at, pnl, pnl_pct
FROM trade_log
WHERE is_paper = TRUE AND exit_at IS NOT NULL
ORDER BY pnl DESC
LIMIT 10;
```

### Progress toward $1M goal
```sql
WITH latest AS (
    SELECT equity, cumul_return_pct, goal_progress_pct, snapshot_date
    FROM account_snapshots ORDER BY snapshot_date DESC LIMIT 1
),
rate AS (
    SELECT AVG(daily_return_pct) AS avg_daily_return
    FROM account_snapshots
    WHERE snapshot_date >= current_date - INTERVAL '30 days'
)
SELECT
    latest.equity                                                    AS current_equity,
    ROUND(latest.cumul_return_pct * 100, 2) || '%'                  AS total_return,
    ROUND(latest.goal_progress_pct * 100, 2) || '%'                 AS goal_progress,
    1000000 - latest.equity                                          AS remaining_to_goal,
    ROUND(rate.avg_daily_return * 100, 3) || '%'                    AS avg_daily_return_30d,
    CASE WHEN rate.avg_daily_return > 0
         THEN CEIL(LN(1000000.0 / latest.equity) /
                   LN(1 + rate.avg_daily_return))
         ELSE NULL
    END                                                              AS est_trading_days_to_goal
FROM latest, rate;
```

---

## Pipeline Pattern

```
[nanoquant-alpaca]          → fetch bars + news                (step 1)
[nanoquant-stockfit]        → fetch signals for same symbols   (step 2)
[nanoquant-duckdb]          → store all results                (step 3) ← HERE
[nanoquant-alpaca-trading]  → execution + fills
[nanoquant-duckdb]          → write trade_log + account_snapshots
```

**Standard pipeline run:**
1. `create_session` → get `session_id`
2. Initialize tables if first run
3. INSERT bars, news, signals
4. After execution: INSERT/UPDATE trade_log entries
5. EOD: INSERT account_snapshots, UPDATE strategy_performance
6. Confirm with `SELECT COUNT(*)`
