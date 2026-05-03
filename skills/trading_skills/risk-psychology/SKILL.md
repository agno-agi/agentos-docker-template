---
name: risk-psychology
description: >
  Risk management, position sizing, and trading psychology mastery for day micro-traders.
  Covers the 1% rule, bracket orders, drawdown protocols, daily loss limits, the Big Four
  emotions (fear, greed, FOMO, revenge trading), pre-trade routines, and performance discipline.
  Use when: (1) calculating position size for a trade, (2) setting stop losses and targets,
  (3) managing drawdown or consecutive losses, (4) analyzing emotional trading patterns,
  (5) building pre/post-trade routines, (6) enforcing trading discipline, or (7) recovering
  from revenge trading or FOMO episodes.
---

# Risk Management & Trading Psychology Skill

The three-legged stool of consistent profitability: risk management preserves capital, psychology maintains discipline, and position sizing determines survival during streaks. This skill enforces the mathematical and mental frameworks that separate the 1% from the 80%.

## Position Sizing: The 1% Rule

### Formula
```
Contracts = (Account Size × Risk%) / (Stop Distance in Ticks × Tick Value)
```

**Example**: $5,000 account, 1% risk, MES stop = 10 points ($50 risk per contract)
- Risk amount: $5,000 × 0.01 = $50
- Contracts: $50 / $50 = 1 contract maximum

### Risk Tiers by Experience
| Tier | Risk/Trade | Max Daily | Experience |
|------|-----------|-----------|------------|
| Beginner | 0.5-1% | 2% | <6 months |
| Intermediate | 1% | 3% | 6-12 months |
| Advanced | 1-2% | 5% | 1+ years |

### Never Risk More Than
- 1% per trade (beginner)
- 3% daily maximum (all traders)
- 10% weekly maximum (all traders)

## The 3 Strikes Rule

After **3 consecutive losses**:
1. Stop trading immediately
2. Close platform for minimum 30 minutes
3. Review journal: were losses from bad trades or bad luck?
4. If bad trades: do not resume until tomorrow
5. If bad luck: resume with 50% normal size

## Bracket Order Setup

Every trade MUST have:
- Entry order (limit or market)
- Stop loss (OCO — One Cancels Other)
- Target (OCO)
- **No manual stop management during the trade**

## Daily Loss Limit Protocol

| Loss Level | Action |
|------------|--------|
| 1% | Yellow flag — review next trade carefully |
| 2% | Orange flag — reduce size 50%, only A+ setups |
| 3% | RED FLAG — stop trading for the day |

## Drawdown Recovery Math

- 10% drawdown requires 11% gain to recover
- 20% drawdown requires 25% gain to recover
- 50% drawdown requires **100%** gain to recover
- **Rule**: Reduce size 50% at 5% drawdown. Stop at 10%.

## The Big Four Emotions & Antidotes

### Fear (Hesitation, Premature Exits)
- **Tell**: Winners held shorter than losers; realized R < planned R
- **Antidote**: 2-minute pre-trade routine + alert-based management (close the chart)

### Greed (Oversized Positions, Moving Targets)
- **Tell**: Position size 1.5-3x normal on "deviation_from_plan" trades
- **Antidote**: Fixed targets in bracket orders; never modify targets after entry

### FOMO (Chasing Entries, Widening Stops)
- **Tell**: Entry in top 20% of move; stop 2-3x normal width; R:R < 1
- **Antidote**: "Setup Match" checklist — if it doesn't match written plan exactly, NO TRADE

### Revenge Trading (Most Destructive)
- **Tell**: 68% of plan deviations occur within 8 minutes of a loss; 1.4x normal size
- **Antidote**: HARD RULE — close platform for 30 minutes after any loss >1x average. No exceptions.

## The 2-Minute Pre-Trade Routine

1. **Check last 3 trades** — if 2 are losses, flag high emotional risk
2. **Rate state 1-5** — stress, confidence, impulse. 4-5 = do not trade
3. **Verify setup matches plan** — every criterion, no exceptions
4. **Confirm R:R ≥ 1.5** — mathematical filter for quality
5. **Three deep breaths** — 4-7-8 technique (inhale 4, hold 7, exhale 8)
6. **State thesis out loud** — one sentence: "I am taking [setup] because [reason]"

## Post-Trade Review (60 Seconds)

1. Did I follow my plan? (Yes/No only)
2. What emotion was strongest? (Calm/Confident/FOMO/Fear/Greed/Revenge)
3. What would I do differently?

Weekly: Review all "deviation" tagged trades. Target >85% plan adherence.

## Flow State & Session Management

- **Optimal session**: 90 minutes (ultradian rhythm)
- **Break**: 15 minutes between sessions
- **Maximum daily**: 3-4 hours active trading
- **Decision fatigue antidote**: Reduce choices — use checklists, not discretion

## Reference: Deep Research

For cost-of-trading math, Kelly Criterion application, prop firm risk rules, and academic psychology studies, see `references/risk-psych-deep-research.md`.
