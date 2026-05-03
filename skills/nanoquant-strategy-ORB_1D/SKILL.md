---
name: nanoquant-strategy-ORB_1D
description: >
  NanoQuant Opening Range Breakout strategy. Identifies the high/low of the first
  30 minutes of trading (09:30–10:00 ET), then takes a long entry when price breaks
  above the opening range high on volume confirmation. Triggers on: "ORB", "opening
  range breakout", "ORB_1D signal", or when portfolio_manager processes screener signals
  tagged with signal_type: "screener" and direction: "long".
---

# NanoQuant — Strategy: ORB_1D (Opening Range Breakout)

**Strategy tag:** `ORB_1D`
**Direction:** Long only
**Signal source:** Stockfit screener (`signal_type: "screener"`, `direction: "long"`)
**Order type:** Market, day
**Timeframe:** Intraday, close same day or hold overnight max 2 days

---

## Concept

The Opening Range Breakout captures momentum when a stock or ETF clears its first
30-minute high on above-average volume. The opening range (09:30–10:00 ET) establishes
support and resistance. A breakout above the high signals institutional buying and
trend continuation.

---

## Entry Criteria

All conditions must be met before sizing an order:

1. **Opening range defined** — price has traded for at least 30 minutes (enter at 10:01+ ET)
2. **Price above ORB high** — current price > high of 09:30–10:00 candle
3. **Volume confirmation** — volume in the breakout candle >= 1.5x the average volume of prior 5 candles
4. **Trend alignment** — SPY is positive on the day (SPY current > SPY prior close)
5. **Signal strength** — Stockfit screener strength >= 0.70
6. **No existing position** — not already holding this symbol

**Ideal setup:** Gap up at open, tight range 09:30–10:00, clean break above range high with volume surge.

---

## Position Sizing

From `nanoquant-portfolio-manager`:

```
base_allocation = equity * 0.15        # 15% of equity max
if strategy.total_trades < 15:
    base_allocation *= 0.50            # new strategy: half size
if signal.strength >= 0.90:
    base_allocation = min(equity * 0.20, buying_power * 0.25)
notional = round(base_allocation, 2)
```

---

## Exit Rules

Apply in priority order (first trigger wins):

| Trigger | Action | Notes |
|---------|--------|-------|
| Price up > 8% from entry | Sell all — take profit | Hard target |
| Price down > 5% from entry | Sell all — stop loss | Hard stop |
| Held > 2 trading days | Sell all — time stop | ORB is an intraday / short-swing play |
| SPY reverses > -1.5% intraday | Sell all — market regime stop | Protect against broad market reversal |
| Stockfit issues opposing signal (short screener) | Sell all | Signal reversal |

---

## DuckDB Queries

### Load today's ORB_1D signals
```sql
SELECT symbol, signal_date, strength, raw_data
FROM stockfit_signals
WHERE signal_date = current_date
  AND signal_type = 'screener'
  AND direction = 'long'
  AND strength >= 0.70
ORDER BY strength DESC;
```

### Check open ORB_1D positions for exit triggers
```sql
SELECT
    tl.symbol,
    tl.entry_price,
    tl.qty,
    tl.entry_at,
    ap.current_price,
    (ap.current_price - tl.entry_price) / tl.entry_price AS unrealized_pct,
    DATE_DIFF('day', DATE(tl.entry_at), current_date) AS days_held
FROM trade_log tl
JOIN (
    SELECT symbol, unrealized_pl / qty AS current_price  -- proxy; replace with live price
    FROM account_positions                                 -- not a real table; use Alpaca get-positions
) ap ON ap.symbol = tl.symbol
WHERE tl.strategy_tag = 'ORB_1D'
  AND tl.exit_at IS NULL
  AND tl.is_paper = TRUE;
```

### ORB_1D performance summary
```sql
SELECT
    COUNT(*)                                          AS total_trades,
    COUNT(*) FILTER (WHERE pnl > 0)                   AS wins,
    ROUND(COUNT(*) FILTER (WHERE pnl > 0)::DOUBLE / COUNT(*) * 100, 1) AS win_rate_pct,
    ROUND(SUM(pnl), 2)                                AS total_pnl,
    ROUND(AVG(pnl), 2)                                AS avg_pnl,
    ROUND(AVG(pnl_pct) * 100, 2)                      AS avg_return_pct,
    ROUND(MAX(pnl), 2)                                AS best_trade,
    ROUND(MIN(pnl), 2)                                AS worst_trade,
    ROUND(AVG(EPOCH(exit_at - entry_at) / 3600.0), 1) AS avg_hold_hours
FROM trade_log
WHERE strategy_tag = 'ORB_1D'
  AND is_paper = TRUE
  AND exit_at IS NOT NULL;
```

---

## Market Conditions

**Best conditions:**
- High-momentum days (VIX 15–25)
- Strong sector rotation / broad market uptrend
- Earnings catalyst (gap up on strong beat)
- Post-FOMC calm trend days

**Avoid:**
- VIX > 30 (high volatility, false breakouts common)
- SPY down > 1% at open
- Pre-earnings if IV crush risk is high
- Choppy, low-volume tape (summer Fridays, holiday weeks)

---

## Watchlist

Primary ORB candidates (Stockfit screener surfaces these):
`SPY, QQQ, NVDA, TSLA, AAPL, MSFT, META, AMZN, AMD, GOOG`

Screener looks for: prior day range contraction, above-avg pre-market volume, gap > 0.3%.

---

## Skills Used

- `nanoquant-stockfit` — fetch screener signals
- `nanoquant-duckdb` — read signals, write trade_log
- `nanoquant-alpaca-trading` — get-positions for exit checks
