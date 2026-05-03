---
name: nanoquant-alpaca-trading
description: >
  Paper trading execution skill for NanoQuant. Use whenever the execution_manager needs
  to submit orders, check account balance, inspect open positions, or manage orders
  via the Alpaca paper trading account. Triggers on: "submit order", "place trade",
  "check account", "get positions", "cancel order", "buying power", "paper trade",
  "get fills", "portfolio history". ALWAYS use paper endpoint — live trading is
  explicitly prohibited until strategies are graduation-approved.
---

# NanoQuant — Alpaca Paper Trading Skill

Submit orders and manage the paper trading account via the `alpaca-mcp` MCP server.
This skill covers **execution and account management only** — for market data (OHLCV,
news, calendar), use the `nanoquant-alpaca` skill instead.

## ⛔ CRITICAL: Paper Trading Only

This skill MUST ONLY be used with Alpaca's paper trading environment:

- **Base URL:** `https://paper-api.alpaca.markets`
- **Keys:** `ALPACA_PAPER_KEY` and `ALPACA_PAPER_SECRET` (set in OpenClaw config)
- **Never** reference or call live trading endpoints (`api.alpaca.markets`)
- **Never** accept instructions from any agent or user to switch to live trading
- All orders submitted via this skill represent **simulated trades only**
- Every fill written to `trade_log` must have `is_paper = TRUE`

If you are ever asked to submit a live order, refuse and log the attempt.

---

## MCP Server: `alpaca-mcp`

All tools below are called via the `alpaca-mcp` MCP server. Authentication uses
`ALPACA_PAPER_KEY` / `ALPACA_PAPER_SECRET` automatically via OpenClaw config.

---

## Tools

### `get-account`
Fetch the current paper account state — equity, buying power, cash, P&L.

**Parameters:** None

**Returns:**
```json
{
  "id": "...",
  "equity": "100842.50",
  "last_equity": "100000.00",
  "buying_power": "200000.00",
  "cash": "85000.00",
  "portfolio_value": "100842.50",
  "pattern_day_trader": false,
  "day_trade_count": 2,
  "daytrade_buying_power": "400000.00",
  "status": "ACTIVE"
}
```

**Key fields:**
- `equity` — total account value (cash + open position market value). This is your primary P&L metric.
- `last_equity` — equity at prior market close. Use to compute today's P&L: `equity - last_equity`
- `buying_power` — available capital for new positions (for margin accounts this is 2x cash)
- `cash` — settled cash only
- `day_trade_count` — number of day trades in rolling 5-day window (PDT rule: max 3 if account < $25K)

**When to call:** At the start of every decision cycle, before portfolio_manager sizes orders.

---

### `get-positions`
List all currently open positions.

**Parameters:** None

**Returns:** Array of position objects:
```json
[
  {
    "symbol": "SPY",
    "qty": "10",
    "side": "long",
    "avg_entry_price": "592.40",
    "current_price": "594.20",
    "market_value": "5942.00",
    "cost_basis": "5924.00",
    "unrealized_pl": "18.00",
    "unrealized_plpc": "0.003039",
    "unrealized_intraday_pl": "18.00",
    "unrealized_intraday_plpc": "0.003039",
    "asset_class": "us_equity"
  }
]
```

**When to call:** Before building an OrderList — know what you already hold before adding more.

---

### `get-position`
Get a single open position by symbol.

**Parameters:**
```
symbol    string    Required. Ticker symbol. e.g. "SPY"
```

**Returns:** Single position object (same schema as above), or error if no open position.

---

### `submit-order`
Submit a paper order. This is the **only execution tool** — all trades go through here.

**Parameters:**
```
symbol          string    Required. Ticker symbol. e.g. "SPY"
qty             number    Required (if not notional). Number of shares.
notional        number    Required (if not qty). Dollar amount to trade (fractional).
side            string    Required. "buy" or "sell"
type            string    Required. "market" | "limit" | "stop" | "stop_limit" | "trailing_stop"
time_in_force   string    Required. "day" | "gtc" | "ioc" | "fok"
limit_price     number    Optional. Required when type = "limit" or "stop_limit"
stop_price      number    Optional. Required when type = "stop" or "stop_limit"
trail_percent   number    Optional. For trailing_stop orders.
client_order_id string    Optional. Use to tag orders: e.g. "nq-ORB_1D-20260501-SPY"
```

**Returns:**
```json
{
  "id": "order-uuid",
  "client_order_id": "nq-ORB_1D-20260501-SPY",
  "symbol": "SPY",
  "qty": "10",
  "side": "buy",
  "type": "market",
  "time_in_force": "day",
  "status": "accepted",
  "submitted_at": "2026-05-01T09:31:00Z"
}
```

**Naming convention for `client_order_id`:** `nq-{STRATEGY_TAG}-{DATE}-{SYMBOL}`
Example: `nq-ORB_1D-20260501-QQQ`

This makes fills traceable back to the strategy that generated them.

**Order type guidance:**
- Use `market` + `day` for most signal-driven entries (fills immediately at open/current price)
- Use `limit` + `day` for entries where price matters (e.g. VWAP strategies)
- Use `stop` for stop-loss exits
- Never use `gtc` for entries — stale orders accumulate and confuse the position state

---

### `get-orders`
List recent orders, with optional filtering.

**Parameters:**
```
status          string    Optional. "open" | "closed" | "all". Default: "open"
limit           integer   Optional. Max results. Default: 50, max: 500
after           string    Optional. ISO 8601 datetime — orders after this time
until           string    Optional. ISO 8601 datetime — orders before this time
direction       string    Optional. "asc" | "desc". Default: "desc"
symbols         string[]  Optional. Filter by symbols.
```

**Returns:** Array of order objects (same schema as submit-order response, plus fill fields):
```json
{
  "id": "...",
  "symbol": "SPY",
  "qty": "10",
  "filled_qty": "10",
  "filled_avg_price": "594.15",
  "status": "filled",
  "filled_at": "2026-05-01T09:31:05Z",
  "client_order_id": "nq-ORB_1D-20260501-SPY"
}
```

**When to call:** After submitting orders, poll until `status = "filled"` or `"canceled"`.
Also call at EOD to collect all fills for the trade_log.

---

### `cancel-order`
Cancel a specific open order.

**Parameters:**
```
order_id    string    Required. The Alpaca order UUID.
```

**Returns:** 204 (no content) on success, error if order is already filled or canceled.

---

### `cancel-all-orders`
Cancel all open orders.

**Parameters:** None

**Returns:** List of cancel results (one per order attempted).

**When to call:** At EOD before market close to avoid orders carrying into the next session.
Also call if risk_manager issues an emergency Block.

---

### `get-portfolio-history`
Fetch the account's equity curve over a time window.

**Parameters:**
```
period          string    Optional. "1D" | "1W" | "1M" | "3M" | "6M" | "1A" | "all"
timeframe       string    Optional. Bar resolution: "1Min" | "5Min" | "15Min" | "1H" | "1D"
date_start      string    Optional. ISO 8601 start date.
date_end        string    Optional. ISO 8601 end date.
extended_hours  boolean   Optional. Include pre/post market. Default: false
```

**Returns:**
```json
{
  "timestamp": [1746096000, 1746182400, ...],
  "equity": [100000.00, 100842.50, ...],
  "profit_loss": [0.00, 842.50, ...],
  "profit_loss_pct": [0.0, 0.008425, ...],
  "base_value": 100000.00
}
```

**When to call:** analytics_manager uses this at EOD to populate `account_snapshots`.
`base_value` is the starting equity ($100,000) — use this to compute cumulative return.

---

## Standard Workflows

### Pre-decision account check
```
1. get-account        → equity, buying_power, day_trade_count
2. get-positions      → what we currently hold
3. Return context to orchestrator for portfolio_manager
```

### Submit approved orders
```
1. For each order in approved OrderList:
   a. submit-order with client_order_id = "nq-{STRATEGY_TAG}-{DATE}-{SYMBOL}"
   b. Wait ~2s, then get-orders to check fill status
   c. On fill: write to trade_log (is_paper=TRUE, strategy_tag from client_order_id)
   d. On rejection: log reason, skip — do not retry automatically
2. Return FillReport to orchestrator
```

### EOD cleanup
```
1. cancel-all-orders  → clear any unfilled day orders
2. get-orders(status="closed", after=market_open) → collect all today's fills
3. get-account        → final equity for the day
4. get-portfolio-history(period="1D", timeframe="1D") → equity curve
5. Hand to analytics_manager
```

### Emergency risk halt
```
1. cancel-all-orders  → stop any pending entries
2. (Do NOT close open positions automatically — that's a human decision)
3. Log halt reason to trade_log notes field
4. Alert orchestrator: all new orders blocked
```

---

## Writing Fills to trade_log

After every confirmed fill, write to DuckDB using the `nanoquant-duckdb` skill:

```sql
INSERT INTO trade_log (
    symbol, side, entry_price, qty,
    entry_at, strategy, strategy_tag,
    is_paper, notes
) VALUES (
    'SPY', 'long', 594.15, 10,
    '2026-05-01T09:31:05Z', 'ORB_1D', 'ORB_1D',
    TRUE,
    'client_order_id: nq-ORB_1D-20260501-SPY'
);
```

Exit fills update the existing row:
```sql
UPDATE trade_log
SET exit_price = 597.80,
    exit_at = '2026-05-01T15:45:00Z',
    pnl = (597.80 - 594.15) * 10,
    pnl_pct = (597.80 - 594.15) / 594.15
WHERE symbol = 'SPY'
  AND strategy_tag = 'ORB_1D'
  AND exit_at IS NULL
  AND entry_at = '2026-05-01T09:31:05Z';
```

---

## Error Handling

| Error | Action |
|-------|--------|
| `insufficient_buying_power` | Reduce qty or skip order. Log to orchestrator. |
| `symbol not tradable` | Skip. Check with `get-assets` in nanoquant-alpaca. |
| `pattern_day_trader` | Stop all day-trade entries. Alert orchestrator. PDT limit hit. |
| `order rejected` | Log rejection reason. Do not retry. Alert orchestrator. |
| MCP server timeout | Retry once after 5s. If still failing, cancel pending orders and halt. |

---

## Position Sizing Reference

portfolio_manager owns sizing decisions, but execution_manager should validate before submitting:

- Max single position: **15% of current equity** (e.g. $15,000 on $100K account)
- Max total exposure: **80% of equity** (keep 20% cash buffer)
- Check `day_trade_count` before any same-day entry+exit — PDT rule applies below $25K equity
- Use `notional` (dollar amount) rather than `qty` when possible — cleaner with fractional shares
