---
name: strategy-orb
description: >
  Opening Range Breakout (ORB) strategy mastery for day micro-trading futures (MES, MNQ, ES, NQ).
  Provides precise entry rules, stop placement, target management, and performance statistics for the
  most backtested intraday breakout strategy. Use when: (1) analyzing opening session trades,
  (2) setting up ORB alerts or scan conditions, (3) backtesting ORB variations, (4) refining
  opening-range trade execution, (5) teaching ORB mechanics, or (6) comparing ORB performance
  across timeframes (5-min, 15-min, 30-min, 60-min).
---

# Opening Range Breakout (ORB) Strategy Skill

Execute Opening Range Breakout trades with statistical precision. ORB is the most backtested intraday strategy, capturing the directional commitment established in the first minutes of the cash session open.

## Core Strategy Rules

### 15-Minute ORB (Recommended for MES/MNQ)

1. **Define the Range**: Mark the high and low of the first 15 minutes after 9:30 AM ET open.
2. **Entry**: Place stop orders at OR high (long) and OR low (short). Trigger on candle CLOSE outside the range — not just wick penetration.
3. **Stop Loss**: Opposite side of the opening range. ~4-10 points on NQ, ~2-5 points on ES.
4. **Target**: TP1 at 1.0R, TP2 at 1.5R-2.0R. Scale out 50% at TP1, trail remainder.
5. **Volume Filter**: Require RVOL > 1.5 (volume expansion confirms breakout validity).
6. **VIX Filter**: Do not trade ORB when VIX > 30 (chop/whiplash risk).
7. **Time Stop**: If trade does not move within 15 minutes, exit at breakeven or small loss.

### 5-Minute ORB (Aggressive Scalping)

- Tighter range, more signals, lower win rate (~58%).
- Best for MNQ with 1-2 point targets.
- Requires faster execution and tighter risk control.

### 60-Minute ORB (0DTE / Credit Spread)

- Widest range, highest win rate (~89.4% on SPX options).
- Profit factor 1.44, average win $39/trade.
- Captures the full morning directional commitment.

## Performance Benchmarks

| Timeframe | Win Rate | Profit Factor | Best Market | Notes |
|-----------|----------|---------------|-------------|-------|
| 5-min | 56-58% | 1.2-1.3 | MNQ | Most signals, highest noise |
| 15-min | 60-64% | 1.3-1.4 | MNQ, MES | Best balance |
| 30-min | 58-60% | 1.2-1.3 | MES | Fewer signals, cleaner |
| 60-min | 82-89% | 1.4-1.5 | SPX options | Widest range, highest WR |

## Failure/Management Rules

- **ORB Fade**: If price breaks OR then immediately reverses with TICK divergence, fade the breakout.
- **No Follow-Through**: If price breaks OR but volume does not expand (RVOL < 1.2), exit quickly.
- **Friday Filter**: Avoid ORB on Fridays if backtest shows underperformance.
- **Post-Event**: Do not trade ORB within 30 minutes after NFP/FOMC/CPI releases.

## Advanced Filters

- **NR7/IDnr4**: Only trade ORB after a volatility contraction day (narrow range day prior).
- **ADD Confirmation**: Require NYSE ADD > 0 for longs, < 0 for shorts.
- **Multi-Timeframe**: Daily chart must not show strong opposing structure at OR level.

## Reference: ORB Deep Research

For backtest details, Toby Crabel original methodology, optimization studies, and conflict-zone analysis, see `references/orb-deep-research.md`.
