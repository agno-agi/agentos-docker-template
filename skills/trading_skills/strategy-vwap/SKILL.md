---
name: strategy-vwap
description: >
  VWAP (Volume Weighted Average Price) strategy mastery for day micro-trading futures. Covers
  VWAP pullback entries, mean reversion at standard deviation bands, opening auction setups,
  and trend continuation trades. Use when: (1) analyzing VWAP-based entries or exits,
  (2) setting VWAP alerts or scan conditions, (3) trading standard deviation band reversions,
  (4) determining institutional fair value positioning, (5) teaching VWAP mechanics,
  or (6) backtesting VWAP strategies on MES/MNQ/ES/NQ.
---

# VWAP Strategy Skill

Execute VWAP-based trades using institutional benchmark behavior. VWAP is the most-used intraday benchmark among institutional traders — it represents the price at which the majority of volume has transacted, creating a "center of gravity" that price tends to revert toward.

## Core Strategy Rules

### Strategy A: VWAP Pullback (Trend Continuation)

1. **Context**: Price is above VWAP in an uptrend (or below in downtrend).
2. **Setup**: Price pulls back to touch or slightly penetrate VWAP.
3. **Entry**: First candle that closes back in the direction of the trend after touching VWAP.
4. **Stop**: Below the VWAP touch low (or above for shorts) — typically 4-8 ticks on MES.
5. **Target**: Next extension or 1.5R-2R. Trail with 9 EMA on 1-min.
6. **Best Time**: After 10:30 AM when VWAP has stabilized.
7. **Avoid**: First 15 minutes (VWAP is too volatile and unreliable).

### Strategy B: VWAP Mean Reversion (Standard Deviation Bands)

1. **Context**: Price has extended significantly from VWAP in a range-bound market (ADX < 20).
2. **Setup**: Price reaches ±2 standard deviation band from VWAP.
3. **Entry**: Reversal candle pattern at the ±2σ band (pin bar, engulfing, or inside bar breakout).
4. **Stop**: Beyond the ±3σ band or the swing extreme.
5. **Target**: VWAP line (1R) or opposite ±1σ band (1.5R).
6. **Probability**: ~95% of price action occurs within ±2σ (normal distribution assumption).
7. **Critical Filter**: Only trade mean reversion when ADX < 20. In trends, VWAP bands fail.

### Strategy C: Opening Auction VWAP

1. **Context**: First 30 minutes after open — VWAP is being established.
2. **Setup**: Price makes an initial directional move, then reverses toward the developing VWAP.
3. **Entry**: First close back toward VWAP after the opening drive.
4. **Use**: Captures the "opening drive exhaustion" pattern.
5. **Risk**: Higher — VWAP is still developing. Reduce size 50%.

## Key Statistics

| Setup | Win Rate | R:R | Best Time | Required Filter |
|-------|----------|-----|-----------|-----------------|
| VWAP Pullback (trend) | 60-65% | 1.5:1 to 2:1 | After 10:30 AM | ADX > 25 |
| ±2σ Mean Reversion | 60-70% | 1:1 to 1.5:1 | Afternoon | ADX < 20 |
| Opening Auction | 55-60% | 1:1 | 9:45-10:30 AM | VIX < 25 |

## VWAP Standard Deviation Band Rules

- **±1σ**: ~68% of price action. Minor resistance/support.
- **±2σ**: ~95% of price action. Primary mean reversion zone. **The trade zone.**
- **±3σ**: ~99.7% of price action. Extreme — only trade with confirmation.

## Afternoon VWAP Reliability

VWAP becomes more reliable as the day progresses:
- 9:30-10:00 AM: VWAP is rapidly moving, unreliable.
- 10:00-11:00 AM: VWAP stabilizing, usable with caution.
- 11:00 AM-2:00 PM: VWAP is flat, most reliable for mean reversion.
- 2:00-4:00 PM: VWAP may shift on news, monitor VIX.

## Reference: VWAP Deep Research

For backtest results, standard deviation statistics, volatility regime adaptation, and academic foundations, see `references/vwap-deep-research.md`.
