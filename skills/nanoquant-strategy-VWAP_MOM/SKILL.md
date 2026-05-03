---
name: nanoquant-strategy-VWAP_MOM
description: >
  NanoQuant VWAP Momentum strategy. Enters long when price reclaims VWAP (Volume
  Weighted Average Price) from below on increasing volume, signaling intraday momentum
  shift. Uses a limit order at or near VWAP. Intraday — closes by end of day.
  Triggers on: "VWAP momentum", "VWAP_MOM signal", or when portfolio_manager processes
  Stockfit signals with signal_type: "momentum" and direction: "long".
---

# NanoQuant — Strategy: VWAP_MOM (VWAP Momentum Long)

**Strategy tag:** `VWAP_MOM`
**Direction:** Long
**Signal source:** Stockfit (`signal_type: "momentum"`, `direction: "long"`)
**Order type:** Limit at VWAP, day (closes same day)
**Timeframe:** Intraday — never hold overnight

---

## Concept

VWAP (Volume Weighted Average Price) is the institutional benchmark for intraday fair
value. When price dips below VWAP and then reclaims it with volume, it signals that
buyers are asserting control. This is an intraday momentum re-entry — not a breakout,
but a trend continuation after a brief pullback.

**Entry:** Limit order at VWAP (or up to 0.1% above)
**Target:** 2–4% move toward the day's high
**Stop:** Price closes back below VWAP on a 5-min candle

---

## Entry Criteria

1. **VWAP reclaim** — price was below VWAP, now crossed back above on a 5-min candle close
2. **Volume spike** — the reclaim candle volume >= 1.2x prior 5-candle average
3. **Time window** — enter only between 10:00–13:30 ET (avoid first 30 min chop and afternoon drift)
4. **Trend context** — stock up > 0.5% on the day before the dip (was already in an uptrend)
5. **SPY positive** — SPY above its intraday VWAP at time of entry
6. **Signal strength** — Stockfit momentum strength >= 0.70
7. **No existing position** — not already held

**Limit order placement:**
```
limit_price = vwap_at_signal_time * 1.001    # 0.1% above VWAP to get filled
```

---

## Position Sizing

```
base_allocation = equity * 0.12        # 12% of equity — slightly smaller (intraday risk)
if strategy.total_trades < 15:
    base_allocation *= 0.50
if signal.strength >= 0.90:
    base_allocation = min(equity * 0.15, buying_power * 0.20)
```

---

## Exit Rules

**All VWAP_MOM positions must be closed by 15:55 ET (5 min before close) — no overnight holds.**

| Trigger | Action | Notes |
|---------|--------|-------|
| Price up > 3% from entry | Sell all — take profit | Intraday target |
| 5-min candle closes below VWAP | Sell all — stop | Momentum failed |
| Price down > 3% from entry | Sell all — stop loss | Hard stop |
| 15:55 ET | Sell all — EOD forced close | Never hold overnight |
| SPY breaks below intraday VWAP | Sell all — macro stop | |

---

## DuckDB Queries

### Load today's VWAP_MOM signals
```sql
SELECT symbol, signal_date, strength, raw_data
FROM stockfit_signals
WHERE signal_date = current_date
  AND signal_type = 'momentum'
  AND direction = 'long'
  AND strength >= 0.70
ORDER BY strength DESC
LIMIT 5;
```

### Open VWAP_MOM positions (check for EOD force-close)
```sql
SELECT
    symbol,
    entry_price,
    qty,
    entry_at,
    EXTRACT(HOUR FROM entry_at AT TIME ZONE 'America/New_York') AS entry_hour_et
FROM trade_log
WHERE strategy_tag = 'VWAP_MOM'
  AND exit_at IS NULL
  AND is_paper = TRUE
  AND DATE(entry_at) = current_date;
-- If any rows returned after 15:55 ET → force close immediately
```

### VWAP_MOM intraday performance by entry time
```sql
SELECT
    EXTRACT(HOUR FROM entry_at AT TIME ZONE 'America/New_York') AS entry_hour_et,
    COUNT(*)                                                     AS trades,
    ROUND(AVG(pnl_pct) * 100, 2)                               AS avg_return_pct,
    ROUND(COUNT(*) FILTER (WHERE pnl > 0)::DOUBLE / COUNT(*) * 100, 1) AS win_rate_pct
FROM trade_log
WHERE strategy_tag = 'VWAP_MOM'
  AND is_paper = TRUE
  AND exit_at IS NOT NULL
GROUP BY entry_hour_et
ORDER BY entry_hour_et;
```

---

## Market Conditions

**Best conditions:**
- Trending day (directional, not choppy)
- VIX 14–22
- Strong pre-market momentum in the name
- Clear sector leadership
- 10:30–13:00 ET window (best VWAP momentum setups)

**Avoid:**
- Choppy, back-and-forth price action (VWAP tag-and-reject pattern)
- VIX > 28
- After 14:00 ET (late-day VWAP momentum unreliable)
- News/earnings pending same day

---

## VWAP Reference

VWAP is not stored in DuckDB — it is a live intraday calculation. The Stockfit signal
includes VWAP in `raw_data.vwap`. Use that value for limit order placement.

Example `raw_data`:
```json
{
  "vwap": 442.18,
  "rsi_5m": 54.2,
  "volume_ratio": 1.4,
  "trend": "above_vwap"
}
```

---

## Skills Used

- `nanoquant-stockfit` — fetch momentum signals with live VWAP
- `nanoquant-duckdb` — read signals, write trade_log
- `nanoquant-alpaca-trading` — submit limit orders, monitor fills, EOD force-close
