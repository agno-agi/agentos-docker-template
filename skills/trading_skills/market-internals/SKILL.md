---
name: market-internals
description: >
  Market internals mastery for day micro-trading futures. Covers NYSE TICK, NYSE ADD (Advance-Decline),
  VIX volatility index, TRIN Arms Index, and top-down multi-timeframe analysis. Use when:
  (1) filtering trade setups with market-wide context, (2) determining if a breakout has breadth
  confirmation, (3) reading TICK extremes for exhaustion signals, (4) using VIX to adjust position
  size, (5) interpreting NYSE ADD divergence, (6) building a market context checklist, or
  (7) deciding whether to trade aggressively or defensively.
---

# Market Internals & Context Skill

Market internals are the "vote count" behind price moves. Price is the headline; internals tell you whether the move is broad and healthy or narrow and fragile. This skill provides a dashboard framework for filtering trades and adjusting aggression levels.

## The Core Trio: TICK + ADD + VIX

### NYSE $TICK Index

Measures NYSE upticks vs. downticks. Oscillates around 0.

| TICK Reading | Interpretation | Trading Action |
|-------------|----------------|----------------|
| > +1000 | Extreme buying, exhaustion likely | Prepare fade; tighten long stops |
| +500 to +800 | Healthy buying pressure | Confirm longs; normal operation |
| -500 to +500 | Neutral/choppy | Reduce size; wait for clarity |
| -500 to -800 | Healthy selling pressure | Confirm shorts; normal operation |
| < -1000 | Extreme selling, exhaustion likely | Prepare fade; tighten short stops |

**Key Signal: TICK Divergence**
- Price makes new high, TICK does NOT = weakening thrust = warning
- Price makes new low, TICK does NOT = selling exhaustion = potential reversal
- Divergence is a **risk flag**, not an automatic entry. Wait for price confirmation.

**TICK Extreme Fade Setup**
- Wait for TICK to hit ±1000
- Look for reversal candle at key price level
- Enter fade with stop beyond the extreme
- Target: nearest support/resistance or VWAP
- Win rate: ~60% with confirmation

### NYSE $ADD (Advance-Decline)

Measures advancing vs. declining NYSE stocks.

| ADD Reading | Market Condition |
|------------|------------------|
| > +1000 | Broad-based strength |
| +200 to +1000 | Moderate strength |
| -200 to +200 | Mixed/uncertain |
| -200 to -1000 | Moderate weakness |
| < -1000 | Broad-based weakness |

**Key Principle**: Zero line is the bull/bear divider.
- Positive ADD on price breakout = healthy, trade aggressively
- Negative ADD on price breakout = fragile, reduce size or skip
- ADD trend vs. price trend divergence = major warning

### VIX (Volatility Index)

Measures expected 30-day S&P 500 volatility. The "fear gauge."

| VIX Level | Regime | Position Size | Stop Width | Strategy |
|-----------|--------|--------------|------------|----------|
| < 15 | Compression | Normal | Normal | Breakout strategies |
| 15-20 | Normal | Normal | Normal | All strategies |
| 20-30 | Elevated | Reduce 25% | Widen 25% | Mean reversion preferred |
| 30-40 | High | Reduce 50% | Widen 50% | Only A+ setups |
| > 40 | Crisis | Reduce 75% or flat | Wide | Mean reversion only |

**VIX Compression/Expansion Cycle**
- VIX < 15 for >5 days = compression building → expect expansion soon
- VIX spike from 15→25+ = regime change → reduce size immediately
- VIX declining from high = trend-friendly environment

## The 2-Out-of-3 Rule

Before taking ANY trade, confirm at least 2 of 3 factors:
1. **Price Structure** — Setup matches plan (support/resistance, pattern)
2. **Breadth (ADD)** — Direction aligns with market breadth
3. **Pressure (TICK)** — TICK confirms direction

| Price | ADD | TICK | Verdict |
|-------|-----|------|---------|
| Breakout Long | Positive | Positive | GO — all align |
| Breakout Long | Negative | Positive | CAUTION — mixed breadth |
| Breakout Long | Positive | Negative | SKIP — weak internals |
| Breakout Long | Negative | Negative | AVOID — likely false |

## Top-Down Analysis Framework

**Daily → 4H → 1H → 15M → 5M**

1. **Daily Chart**: Structure, trend direction, key levels. Is today likely trending or ranging?
2. **4H/1H**: Directional bias, support/resistance zones, pattern formations.
3. **15M/5M**: Execution timeframe — entries, stops, targets.

**Rule**: Only take trades that align with the Daily + 1H bias. Counter-trend trades only at extreme levels with TICK divergence.

## Pre-Market Context Checklist

Before 9:30 AM, check:
- [ ] Overnight session high/low (sets initial range)
- [ ] Economic calendar — any Tier 1 events today?
- [ ] VIX closing level and overnight change
- [ ] Asian/European market direction
- [ ] Pre-market earnings or news on major components (AAPL, NVDA, etc.)
- [ ] Daily chart structure — key levels to watch

## Red Flags: Do Not Trade

- VIX > 30 without a clear plan
- TICK oscillating wildly ±800 with no direction (chop)
- ADD near 0 with price making large moves (narrow leadership)
- Major economic release within 30 minutes
- Personal emotional state rated 4-5 (stressed/impulsive)

## Reference: Internals Deep Research

For institutional weighted scoring models, advanced divergence setups, and academic studies on market breadth, see `references/internals-deep-research.md`.
