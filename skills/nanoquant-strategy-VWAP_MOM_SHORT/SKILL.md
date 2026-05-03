---
name: nanoquant-strategy-VWAP_MOM_SHORT
description: >
  NanoQuant VWAP Momentum Short strategy. Enters short when price rejects VWAP from
  above (loses VWAP) on increasing volume, signaling intraday momentum shift to the
  downside. Limit order at or near VWAP. Intraday — closes same day. Triggers on:
  "VWAP momentum short", "VWAP_MOM_SHORT signal", or when portfolio_manager processes
  Stockfit signals with signal_type: "momentum" and direction: "short".
---

# NanoQuant — Strategy: VWAP_MOM_SHORT (VWAP Momentum Short)

**Strategy tag:** `VWAP_MOM_SHORT`
**Direction:** Short
**Signal source:** Stockfit (`signal_type: "momentum"`, `direction: "short"`)
**Order type:** Limit at VWAP, day (closes same day)
**Timeframe:** Intraday — never hold overnight

---

## Concept

Mirror of VWAP_MOM but for the downside. When price that was above VWAP loses it and
fails to reclaim on a retest, it signals sellers are in control. Short at the VWAP
rejection — target the day's low or a 2–3% move down.

**Entry:** Limit short order at VWAP (or up to 0.1% below)
**Target:** 2–3% move toward the day's low
**Stop:** Price closes back above VWAP on a 5-min candle

---

## Entry Criteria

1. **VWAP loss** — price was above VWAP, crossed below, then bounced to retest VWAP from below
2. **Failed reclaim** — the retest candle closes below VWAP (rejection)
3. **Volume** — rejection candle volume >= 1.2x prior 5-candle average
4. **Time window** — enter only between 10:30–14:00 ET
5. **Trend context** — stock down > 0.5% on the day before the bounce (was already weak)
6. **SPY weak** — SPY below its intraday VWAP at time of entry
7. **Signal strength** — Stockfit momentum strength >= 0.70

**Limit order placement:**
```
limit_price = vwap_at_signal_time * 0.999    # 0.1% below VWAP to short into the move
```

---

## Position Sizing

```
base_allocation = equity * 0.10        # 10% — smaller than long VWAP (short is riskier intraday)
if strategy.total_trades < 15:
    base_allocation *= 0.50
```

---

## Exit Rules

**All VWAP_MOM_SHORT positions must be closed by 15:55 ET — no overnight holds.**

| Trigger | Action | Notes |
|---------|--------|-------|
| Price down > 2.5% from entry | Cover all — take profit | Intraday short target |
| 5-min candle closes back above VWAP | Cover all — stop | Momentum failed |
| Price up > 3% from entry (loss) | Cover all — hard stop | |
| 15:55 ET | Cover all — EOD forced close | Never hold overnight |
| SPY reclaims intraday VWAP | Cover all — macro stop | |

---

## DuckDB Queries

### Load today's VWAP_MOM_SHORT signals
```sql
SELECT symbol, signal_date, strength, raw_data
FROM stockfit_signals
WHERE signal_date = current_date
  AND signal_type = 'momentum'
  AND direction = 'short'
  AND strength >= 0.70
ORDER BY strength DESC
LIMIT 5;
```

### All open intraday short positions (check for EOD close)
```sql
SELECT symbol, entry_price, qty, entry_at
FROM trade_log
WHERE strategy_tag = 'VWAP_MOM_SHORT'
  AND side = 'short'
  AND exit_at IS NULL
  AND is_paper = TRUE
  AND DATE(entry_at) = current_date;
```

### VWAP momentum long vs short comparison
```sql
SELECT
    strategy_tag,
    COUNT(*)                                                         AS trades,
    ROUND(AVG(pnl_pct) * 100, 2)                                    AS avg_return_pct,
    ROUND(COUNT(*) FILTER (WHERE pnl > 0)::DOUBLE / COUNT(*) * 100, 1) AS win_rate_pct,
    ROUND(SUM(pnl), 2)                                               AS total_pnl
FROM trade_log
WHERE strategy_tag IN ('VWAP_MOM', 'VWAP_MOM_SHORT')
  AND is_paper = TRUE
  AND exit_at IS NOT NULL
GROUP BY strategy_tag;
```

---

## Market Conditions

**Best conditions:**
- Weak/declining market (SPY below VWAP, trending down)
- VIX 18–30
- Clear sector weakness
- Stock rejected off a key resistance level earlier in the day

**Avoid:**
- VIX < 15 (too bullish, VWAP shorts get squeezed)
- After 14:30 ET (too late for meaningful intraday short)
- High short-interest stocks (squeeze risk)
- Before Fed announcements or major macro events

---

## Skills Used

- `nanoquant-stockfit` — fetch momentum short signals
- `nanoquant-duckdb` — read signals, write trade_log
- `nanoquant-alpaca-trading` — submit limit short orders, EOD force-cover
