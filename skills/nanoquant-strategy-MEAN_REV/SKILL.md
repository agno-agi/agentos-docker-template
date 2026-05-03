---
name: nanoquant-strategy-MEAN_REV
description: >
  NanoQuant Mean Reversion strategy. Buys oversold pullbacks in strong uptrending stocks
  expecting a bounce back toward the mean (20-day SMA or VWAP). Enters via limit order
  at the oversold level. Hold 1–3 days. Triggers on: "mean reversion", "oversold bounce",
  "MEAN_REV signal", or when portfolio_manager processes Stockfit signals with
  signal_type: "mean_reversion" and direction: "long".
---

# NanoQuant — Strategy: MEAN_REV (Mean Reversion Long)

**Strategy tag:** `MEAN_REV`
**Direction:** Long
**Signal source:** Stockfit (`signal_type: "mean_reversion"`, `direction: "long"`)
**Order type:** Limit (at oversold level), day
**Timeframe:** 1–3 trading days

---

## Concept

Mean reversion trades the rubber band effect. Strong stocks don't go straight up —
they pull back 5–10% to the 20-day SMA or VWAP, then recover. The edge: buy fear/panic
in a fundamentally strong uptrend, sell the snap-back. Not a trend continuation play —
this is a counter-trend entry into temporary weakness.

**The setup requires a strong prior trend.** Do NOT mean-revert stocks in confirmed downtrends.

---

## Entry Criteria

1. **Strong prior trend** — stock up > 20% over last 60 days before the pullback
2. **Pullback magnitude** — stock down 5–12% from recent high (over 3–8 trading days)
3. **At or near the mean** — price within 1% of 20-day SMA or 20-day VWAP
4. **Not in free fall** — no high-volume distribution during pullback (normal low-volume drift down)
5. **RSI oversold** — RSI(14) below 40 (ideally 30–38)
6. **SPY stable** — SPY not down > 1.5% on the day (avoid catching falling knife in weak market)
7. **Signal strength** — Stockfit mean_reversion strength >= 0.72

**Limit order placement:**
```
limit_price = min(current_price, 20_day_sma * 1.005)    # buy at or just above 20-day SMA
```

---

## Position Sizing

```
base_allocation = equity * 0.12        # 12% — moderate size (counter-trend = more risk)
if strategy.total_trades < 15:
    base_allocation *= 0.50
# No size-up for high conviction — mean reversion is inherently riskier
```

---

## Exit Rules

| Trigger | Action | Notes |
|---------|--------|-------|
| Price recovers to within 2% of prior high | Sell all — take profit | Snap-back complete |
| Price up > 6% from entry | Sell all — take profit | Hit target |
| Price down > 5% below entry | Sell all — stop loss | Trend is broken, not reverting |
| Held > 3 trading days without 3% gain | Sell all — time stop | If it hasn't bounced, move on |
| Stock breaks 50-day SMA to the downside | Sell all — trend broken | No longer in uptrend |

---

## DuckDB Queries

### Load today's MEAN_REV signals
```sql
SELECT symbol, signal_date, strength, raw_data
FROM stockfit_signals
WHERE signal_date = current_date
  AND signal_type = 'mean_reversion'
  AND direction = 'long'
  AND strength >= 0.72
ORDER BY strength DESC
LIMIT 5;
```

### Compute pullback magnitude from ohlcv_bars
```sql
WITH recent_high AS (
    SELECT symbol, MAX(high) AS high_60d
    FROM ohlcv_bars
    WHERE timeframe = '1Day'
      AND ts >= current_date - INTERVAL '60 days'
    GROUP BY symbol
),
latest AS (
    SELECT symbol, close AS current_close
    FROM ohlcv_bars
    WHERE timeframe = '1Day'
      AND ts = (SELECT MAX(ts) FROM ohlcv_bars WHERE timeframe = '1Day')
)
SELECT
    l.symbol,
    ROUND(l.current_close, 2)                            AS current_price,
    ROUND(rh.high_60d, 2)                                AS high_60d,
    ROUND((l.current_close - rh.high_60d) / rh.high_60d * 100, 1) AS pullback_pct
FROM latest l
JOIN recent_high rh ON rh.symbol = l.symbol
WHERE (l.current_close - rh.high_60d) / rh.high_60d BETWEEN -0.12 AND -0.05
ORDER BY pullback_pct;
```

### MEAN_REV performance by pullback depth
```sql
SELECT
    CASE
        WHEN pnl_pct > 0.05  THEN '>5% gain'
        WHEN pnl_pct > 0.02  THEN '2-5% gain'
        WHEN pnl_pct > 0      THEN '0-2% gain'
        ELSE 'loss'
    END                                                  AS outcome,
    COUNT(*)                                             AS trades,
    ROUND(AVG(pnl), 2)                                  AS avg_pnl
FROM trade_log
WHERE strategy_tag = 'MEAN_REV'
  AND is_paper = TRUE
  AND exit_at IS NOT NULL
GROUP BY outcome;
```

---

## Market Conditions

**Best conditions:**
- Bull market with normal pullbacks (VIX 12–22)
- Stock in confirmed uptrend (above 200-day SMA)
- Pullback on low volume (profit-taking, not distribution)
- Broader market holding key support levels

**Avoid:**
- Bear market or market correction (> -10% from highs)
- Stock below 200-day SMA
- Earnings within 3 days (catalyst risk)
- High-volume selloff during pullback (institutional distribution)
- VIX spiking > 30

---

## Key Insight

The most dangerous trap in mean reversion: buying what looks like a pullback in a
broken stock. Before entering, always verify the 60-day trend is genuinely positive.
A stock down 30% is NOT a mean reversion opportunity — it's a downtrend.

---

## Skills Used

- `nanoquant-stockfit` — fetch mean_reversion signals
- `nanoquant-duckdb` — read signals + ohlcv_bars, write trade_log
- `nanoquant-alpaca-trading` — submit limit orders, get-positions
