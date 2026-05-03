---
name: nanoquant-strategy-BREAKOUT_SHORT
description: >
  NanoQuant Breakout Short strategy. Enters short when a stock breaks DOWN through
  a multi-day support level or key floor on expanding volume. Mirror of BREAKOUT but
  for the downside. Triggers on: "breakout short", "BREAKOUT_SHORT signal", or when
  portfolio_manager processes Stockfit signals with signal_type: "breakout" and
  direction: "short".
---

# NanoQuant — Strategy: BREAKOUT_SHORT (Breakout Short)

**Strategy tag:** `BREAKOUT_SHORT`
**Direction:** Short
**Signal source:** Stockfit (`signal_type: "breakout"`, `direction: "short"`)
**Order type:** Market, day (short sell)
**Timeframe:** Swing — hold 1–5 trading days

---

## Concept

Breakdown trading mirrors breakout trading on the downside. When a stock breaks below
a defined support level (20-day low, multi-week consolidation floor, prior pivot low)
on high volume, it signals institutional distribution and trend continuation downward.
Target: 8–15% decline before next support.

**⚠️ Paper trading only.** Shorting requires margin. All shorts are paper positions
tracked in trade_log with `side = "short"`. Alpaca paper account supports short selling.

---

## Entry Criteria

1. **Price at or below key support** — breaking 20-day low, multi-week base floor, or defined chart level
2. **Volume surge** — breakdown volume >= 1.5x 20-day average daily volume
3. **Signal strength** — Stockfit `strength >= 0.75`
4. **Trend alignment** — SPY below its 20-day SMA OR SPY down > 0.5% on the day
5. **RS check** — stock underperforming SPY over last 10 days (relative weakness)
6. **No existing position** — not already held (long or short)
7. **Not oversold** — RSI not below 25 (avoid shorting into panic-sell exhaustion)

**Ideal setup:** Failed breakout attempt, heavy distribution, breakdown below flat base with volume.

---

## Position Sizing

```
base_allocation = equity * 0.10        # 10% of equity — slightly smaller than longs
                                       # short squeezes can be violent; be conservative
if strategy.total_trades < 15:
    base_allocation *= 0.50
if signal.strength >= 0.90:
    base_allocation = min(equity * 0.15, buying_power * 0.20)
```

---

## Exit Rules

| Trigger | Action | Notes |
|---------|--------|-------|
| Price down > 8% from entry (profit) | Cover half — partial profit | Lock in gains |
| Price down > 15% from entry | Cover all — full profit | Don't get greedy |
| Price up > 4% from entry (loss) | Cover all — stop loss | Short stops are tighter than long stops |
| Close back above breakdown level | Cover all | Failed breakdown |
| Held > 5 trading days without reaching 5% gain | Cover all — time stop | |
| SPY breaks 20-day SMA to the upside | Reduce or exit | Regime change to bullish |
| Short squeeze indicators (volume spike + price reversal) | Cover immediately | Protect capital |

---

## DuckDB Queries

### Load today's BREAKOUT_SHORT signals
```sql
SELECT symbol, signal_date, strength, direction, raw_data
FROM stockfit_signals
WHERE signal_date = current_date
  AND signal_type = 'breakout'
  AND direction = 'short'
  AND strength >= 0.75
ORDER BY strength DESC
LIMIT 5;
```

### Open short positions
```sql
SELECT
    symbol,
    entry_price,
    qty,
    entry_at,
    DATE_DIFF('day', DATE(entry_at), current_date) AS days_held
FROM trade_log
WHERE strategy_tag = 'BREAKOUT_SHORT'
  AND side = 'short'
  AND exit_at IS NULL
  AND is_paper = TRUE
ORDER BY entry_at;
```

### Compare BREAKOUT vs BREAKOUT_SHORT performance
```sql
SELECT
    strategy_tag,
    COUNT(*)                                                AS trades,
    ROUND(AVG(pnl), 2)                                     AS avg_pnl,
    ROUND(COUNT(*) FILTER (WHERE pnl > 0)::DOUBLE / COUNT(*) * 100, 1) AS win_rate_pct,
    ROUND(SUM(pnl), 2)                                     AS total_pnl
FROM trade_log
WHERE strategy_tag IN ('BREAKOUT', 'BREAKOUT_SHORT')
  AND is_paper = TRUE
  AND exit_at IS NOT NULL
GROUP BY strategy_tag;
```

---

## Market Conditions

**Best conditions:**
- Broad market downtrend (SPY below 20-day SMA)
- VIX > 20 and rising
- Sector in confirmed downtrend
- Post-earnings gap down on weak guidance
- Credit spreads widening (risk-off environment)

**Avoid:**
- VIX < 15 (trending bull market — shorts get squeezed)
- Pre-FOMC (unpredictable reversals)
- Heavily shorted stock (high short interest = squeeze risk)
- Thin, illiquid names (hard to cover at a good price)

---

## Risk Note

Short positions have theoretically unlimited loss potential (price can rise without bound).
The risk_manager hard-caps BREAKOUT_SHORT positions at 10% of equity and enforces the
4% stop loss strictly. No exceptions.

---

## Skills Used

- `nanoquant-stockfit` — fetch breakdown signals
- `nanoquant-duckdb` — read signals, write/read trade_log
- `nanoquant-alpaca-trading` — submit short orders, get-positions
