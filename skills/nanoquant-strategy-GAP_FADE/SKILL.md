---
name: nanoquant-strategy-GAP_FADE
description: >
  NanoQuant Gap Fade strategy. Fades (trades against) excessively large overnight gaps
  at the open, expecting them to partially or fully fill during the first 60–90 minutes
  of trading. Enters long on gap-down fades or short on gap-up fades. Intraday only —
  always closes by EOD. Triggers on: "gap fade", "fade the gap", "GAP_FADE signal", or
  when portfolio_manager processes Stockfit signals with signal_type: "gap".
---

# NanoQuant — Strategy: GAP_FADE

**Strategy tag:** `GAP_FADE`
**Direction:** Both (long on gap-down fades, short on gap-up fades)
**Signal source:** Stockfit (`signal_type: "gap"`, `direction: "long"` or `"short"`)
**Order type:** Market, day
**Timeframe:** Intraday — target fill within 60–90 minutes, always close by 15:55 ET

---

## Concept

Most gaps don't hold. Stocks that gap up on earnings/news frequently see profit-taking
as traders sell into strength. Stocks that gap down see dip buyers recover the move.
Gap Fade exploits this: enter into the gap, ride the fill, exit before the next trend
leg takes over.

**Long fade (gap-down):** Buy the panic gap-down, sell when it partially fills.
**Short fade (gap-up):** Short the euphoric gap-up, cover when it fades back.

---

## Entry Criteria (both directions)

1. **Gap size** — gap > 1.5% and < 8% (too small = no edge; too large = dangerous)
2. **Pre-market volume** — pre-market volume < 50% of normal daily volume (not a momentum gap)
3. **No major catalyst** — earnings beats/misses with strong guidance should NOT be faded
   (news-driven gaps can extend; only fade technical/low-news gaps)
4. **Opening momentum fades** — first 5-min candle shows reversal (gap-up opens, first candle red;
   gap-down opens, first candle green)
5. **Signal strength** — Stockfit gap strength >= 0.68
6. **Time of entry** — enter between 09:35–10:00 ET only (first 30 min for gap fades)

### Long fade entry (gap-down):
- Stock gapped down > 1.5%
- First 5-min candle closes green (buyers stepping in)
- Enter market buy at 09:35 ET open of second candle

### Short fade entry (gap-up):
- Stock gapped up > 1.5%
- First 5-min candle closes red (sellers taking profit)
- Enter market short at 09:35 ET open of second candle

---

## Position Sizing

```
base_allocation = equity * 0.10        # 10% — smaller size, gap fades can fail violently
if strategy.total_trades < 15:
    base_allocation *= 0.50
# Never size up gap fades — they're inherently noisy
```

---

## Exit Rules

**Target: partial gap fill (50–75% of the gap closed). Never hold waiting for 100% fill.**

| Trigger | Action | Notes |
|---------|--------|-------|
| 50% gap fill reached | Sell/cover half | Lock in half the profit |
| 75% gap fill reached | Sell/cover all | Full exit at target |
| Gap extends > 2% further in original direction | Exit — stop loss | Gap is continuing, not fading |
| Held > 90 minutes without 1% move toward fill | Exit — time stop | Gap isn't fading today |
| 15:55 ET | Force close all — EOD | Never hold gap fades overnight |

**Gap fill calculation:**
```
prior_close = yesterday's close
gap_open    = today's open
gap_size    = gap_open - prior_close
50pct_fill  = gap_open - (gap_size * 0.50)    # for long fade (gap down)
75pct_fill  = gap_open - (gap_size * 0.75)
```

---

## DuckDB Queries

### Load today's gap signals
```sql
SELECT symbol, signal_date, direction, strength, raw_data
FROM stockfit_signals
WHERE signal_date = current_date
  AND signal_type = 'gap'
  AND strength >= 0.68
ORDER BY strength DESC
LIMIT 5;
```

### Compute gap size from OHLCV bars
```sql
WITH today AS (
    SELECT symbol, open AS today_open
    FROM ohlcv_bars
    WHERE timeframe = '1Day' AND DATE(ts) = current_date
),
yesterday AS (
    SELECT symbol, close AS prior_close
    FROM ohlcv_bars
    WHERE timeframe = '1Day'
      AND DATE(ts) = (SELECT MAX(DATE(ts)) FROM ohlcv_bars
                      WHERE timeframe = '1Day' AND DATE(ts) < current_date)
)
SELECT
    t.symbol,
    ROUND(y.prior_close, 2)                                AS prior_close,
    ROUND(t.today_open, 2)                                 AS today_open,
    ROUND((t.today_open - y.prior_close) / y.prior_close * 100, 2) AS gap_pct,
    CASE WHEN t.today_open > y.prior_close THEN 'gap_up' ELSE 'gap_down' END AS gap_direction
FROM today t
JOIN yesterday y ON y.symbol = t.symbol
WHERE ABS((t.today_open - y.prior_close) / y.prior_close) BETWEEN 0.015 AND 0.08
ORDER BY ABS((t.today_open - y.prior_close) / y.prior_close) DESC;
```

### GAP_FADE performance by gap size
```sql
SELECT
    CASE
        WHEN ABS(CAST(json_extract_string(notes, '$.gap_pct') AS DOUBLE)) < 0.03 THEN '<3% gap'
        WHEN ABS(CAST(json_extract_string(notes, '$.gap_pct') AS DOUBLE)) < 0.05 THEN '3-5% gap'
        ELSE '>5% gap'
    END                                                   AS gap_bucket,
    COUNT(*)                                              AS trades,
    ROUND(AVG(pnl_pct) * 100, 2)                        AS avg_return_pct,
    ROUND(COUNT(*) FILTER (WHERE pnl > 0)::DOUBLE / COUNT(*) * 100, 1) AS win_rate_pct
FROM trade_log
WHERE strategy_tag = 'GAP_FADE'
  AND is_paper = TRUE
  AND exit_at IS NOT NULL
GROUP BY gap_bucket;
```

---

## Market Conditions

**Best conditions:**
- Low/moderate VIX (14–22)
- No major macro events same day (FOMC, CPI, jobs report)
- Gap driven by technical noise, not strong fundamental catalyst
- Mean-reverting tape (not a strong trending day)

**Avoid:**
- Earnings beat/miss with guide raise (gap will continue, not fade)
- VIX > 30 (gaps can be violent)
- Pre-FOMC or major economic data days
- Strong directional trend days (gaps tend to hold)
- Biotech/clinical trial gaps (binary, unpredictable)

---

## Do Not Fade These Gaps

- Earnings beats with raised guidance → continuation, not fade
- Acquisition/merger announcements → gap holds
- FDA approvals (biotech) → binary, not a fade setup
- Index rebalancing adds/removals → institutional demand holds the move
- Short squeeze in progress → gap will extend, not fade

---

## Skills Used

- `nanoquant-stockfit` — fetch gap signals
- `nanoquant-duckdb` — read signals + ohlcv_bars for gap calculation, write trade_log
- `nanoquant-alpaca-trading` — submit market orders (both sides), force EOD close
