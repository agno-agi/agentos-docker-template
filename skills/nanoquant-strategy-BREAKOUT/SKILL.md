---
name: nanoquant-strategy-BREAKOUT
description: >
  NanoQuant Breakout strategy. Enters long when a stock breaks above a multi-day
  consolidation zone or key resistance level on expanding volume. Swing trade bias:
  holds 1–5 days targeting 8–15% moves. Triggers on: "breakout long", "BREAKOUT signal",
  or when portfolio_manager processes Stockfit signals with signal_type: "breakout"
  and direction: "long".
---

# NanoQuant — Strategy: BREAKOUT (Breakout Long)

**Strategy tag:** `BREAKOUT`
**Direction:** Long
**Signal source:** Stockfit (`signal_type: "breakout"`, `direction: "long"`)
**Order type:** Market, day
**Timeframe:** Swing — hold 1–5 trading days

---

## Concept

Breakout trading captures the explosive move when a stock clears a defined resistance
level (52-week high, multi-week consolidation top, prior pivot) on volume. The thesis:
institutional accumulation during the base, then aggressive buying on the breakout.
Target: 8–15% move before the next resistance zone.

---

## Entry Criteria

1. **Price at or above key resistance** — breaking 20-day high, 52-week high, or defined chart level
2. **Volume surge** — breakout volume >= 1.5x 20-day average daily volume
3. **Signal strength** — Stockfit `strength >= 0.75` (higher bar than ORB — swing trades carry overnight risk)
4. **Trend alignment** — SPY above its 20-day SMA (confirmed uptrend)
5. **RS check** — stock outperforming SPY over last 10 days
6. **No existing position** — not already held
7. **Not extended** — price not > 10% above the consolidation base (chasing is risky)

**Ideal setup:** 3–8 week flat base, tight weekly closes, low-volume contraction then explosive-volume breakout.

---

## Position Sizing

```
base_allocation = equity * 0.15        # 15% of equity — full size for proven strategy
if strategy.total_trades < 15:
    base_allocation *= 0.50            # half size until 15 trades established
if signal.strength >= 0.90:
    base_allocation = min(equity * 0.20, buying_power * 0.25)
```

---

## Exit Rules

| Trigger | Action | Notes |
|---------|--------|-------|
| Price up > 8% from entry | Sell half — partial profit | Let runners run |
| Price up > 15% from entry | Sell remaining — full exit | Full profit target |
| Price down > 5% from entry | Sell all — stop loss | Cut losses fast |
| Close below breakout level (intraday reclaim OK) | Sell all | Failed breakout |
| Held > 5 trading days without reaching 5% gain | Sell all — time stop | Move capital |
| SPY breaks 20-day SMA to the downside | Reduce to half or exit | Macro regime change |

---

## DuckDB Queries

### Load today's BREAKOUT signals
```sql
SELECT symbol, signal_date, strength, direction, raw_data
FROM stockfit_signals
WHERE signal_date = current_date
  AND signal_type = 'breakout'
  AND direction = 'long'
  AND strength >= 0.75
ORDER BY strength DESC
LIMIT 5;
```

### Open BREAKOUT positions + exit check
```sql
SELECT
    symbol,
    entry_price,
    qty,
    entry_at,
    DATE_DIFF('day', DATE(entry_at), current_date) AS days_held,
    notes
FROM trade_log
WHERE strategy_tag = 'BREAKOUT'
  AND exit_at IS NULL
  AND is_paper = TRUE
ORDER BY entry_at;
```

### BREAKOUT performance by holding period
```sql
SELECT
    CASE
        WHEN EPOCH(exit_at - entry_at) / 3600.0 <= 8   THEN 'same-day'
        WHEN EPOCH(exit_at - entry_at) / 3600.0 <= 32  THEN '1-day'
        WHEN EPOCH(exit_at - entry_at) / 3600.0 <= 80  THEN '2-4 days'
        ELSE '5+ days'
    END                                              AS hold_bucket,
    COUNT(*)                                         AS trades,
    ROUND(AVG(pnl_pct) * 100, 2)                    AS avg_return_pct,
    ROUND(COUNT(*) FILTER (WHERE pnl > 0)::DOUBLE / COUNT(*) * 100, 1) AS win_rate_pct
FROM trade_log
WHERE strategy_tag = 'BREAKOUT'
  AND is_paper = TRUE
  AND exit_at IS NOT NULL
GROUP BY hold_bucket
ORDER BY avg_return_pct DESC;
```

---

## Market Conditions

**Best conditions:**
- Broad market uptrend (SPY above 20-day SMA)
- Low VIX (< 20) — trend-following environment
- Strong sector leadership (leading sector breaking out with the stock)
- Post-earnings gap on strong guidance

**Avoid:**
- VIX > 25
- SPY in a downtrend or below 200-day SMA
- Earnings within 5 days (IV risk)
- Market-wide distribution days (4+ distribution days in 5 sessions)

---

## Skills Used

- `nanoquant-stockfit` — fetch breakout signals
- `nanoquant-duckdb` — read signals, write/read trade_log
- `nanoquant-alpaca-trading` — submit orders, get-positions
