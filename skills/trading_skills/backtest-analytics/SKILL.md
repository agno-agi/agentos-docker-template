---
name: backtest-analytics
description: >
  Backtesting, trade journaling, and performance analytics for day micro-traders. Covers walk-forward
  analysis, Monte Carlo simulation, key metrics (win rate, profit factor, expectancy, Sharpe),
  trade journaling systems, strategy degradation detection, and personal playbook development.
  Use when: (1) validating a new strategy before going live, (2) analyzing personal trading
  performance data, (3) setting up a journaling system, (4) detecting if a strategy has stopped
  working, (5) calculating expectancy or profit factor, or (6) building a personal trading playbook.
---

# Backtesting & Performance Analytics Skill

Data beats intuition. This skill provides the systematic framework for validating strategies, tracking performance, detecting edge degradation, and building a personal playbook based on statistical evidence rather than feelings.

## Key Performance Metrics

### Expectancy (The Most Important Number)
```
Expectancy = (Win Rate × Average Win) - (Loss Rate × Average Loss)
```

**Benchmarks by Style**:
| Style | Expectancy per Trade |
|-------|---------------------|
| Scalper | $15-80 |
| Day Trader | $40-150 |
| Swing Trader | $60-200 |

**Rule**: If expectancy is negative or zero after 50+ trades, the strategy is broken or unprofitable after costs.

### Profit Factor
```
Profit Factor = Gross Profit / Gross Loss
```
| PF Range | Interpretation |
|----------|---------------|
| < 1.0 | Losing strategy |
| 1.0-1.3 | Marginal, probably unprofitable after costs |
| 1.3-1.6 | Viable with good execution |
| 1.6-2.0 | Strong edge |
| > 2.0 | Exceptional (verify for curve-fitting) |

### Win Rate vs. R:R Relationship
| Win Rate | Required R:R for Breakeven (after costs) |
|----------|----------------------------------------|
| 80% | 0.3:1 |
| 70% | 0.6:1 |
| 60% | 0.9:1 |
| 50% | 1.3:1 |
| 40% | 2.0:1 |
| 30% | 3.3:1 |

**Key Insight**: A 50% WR with 2:1 R:R is more robust than 70% WR with 0.5:1 R:R. R:R provides margin of safety.

### Sharpe & Sortino Ratios
- **Sharpe > 1.0**: Good risk-adjusted returns
- **Sharpe > 2.0**: Excellent
- **Sortino > 1.5**: Good downside-adjusted returns

### Maximum Consecutive Losers
- Know your max losing streak from backtest
- Size positions to survive 2x that streak
- Mental preparation: if backtest shows 6 consecutive losers, expect 12 in live trading

## Backtesting Protocol

### Phase 1: Manual Backtest (Bar-by-Bar)
- Use TradingView replay mode or NinjaTrader Market Replay
- Log minimum 50 trades (100+ preferred)
- Record: setup type, entry, stop, target, outcome, emotion, market condition
- **Goal**: Prove the strategy works on historical data

### Phase 2: Automated Backtest
- Code strategy in Pine Script (TradingView) or NinjaScript
- Test on 2+ years of data
- Include realistic commissions and slippage
- **Goal**: Validate edge with statistical significance

### Phase 3: Walk-Forward Analysis (Gold Standard)
1. Split data: 60-80% in-sample, 20-30% out-of-sample
2. Optimize on in-sample only
3. Test optimized rules on out-of-sample
4. Walk-forward efficiency (WFE) > 50% = robust strategy
5. **Critical**: Studies show after testing 7 strategy configs, a 2-year backtest with Sharpe > 1 may have out-of-sample Sharpe = 0

### Phase 4: Monte Carlo Simulation
- Reshuffle trade sequences 5,000+ times
- Reveals full distribution of possible outcomes
- Key insight: 8% backtest max DD might be 18% at 90th percentile
- Use 90th percentile DD for position sizing, not backtest point estimate

### Phase 5: Paper Trade
- Minimum 30 days live simulation
- Win rate within 5-10% of backtest = good
- Rule adherence >80% before going live

## Strategy Health Monitor

### Green (Continue Normal Operation)
- Win rate within 5% of baseline
- Positive expectancy maintained
- Max DD < 5%
- Profit factor > 1.3

### Yellow (Reduce Size 50%)
- Win rate down 5-10%
- Expectancy declining but still positive
- Max DD 5-10%
- Profit factor 1.0-1.3

### Red (STOP — Re-evaluate)
- Win rate down >10%
- Negative expectancy for 2+ weeks
- Max DD > 10%
- Profit factor < 1.0

## Trade Journaling System

### What to Log (Every Trade)
1. Date/time, symbol, setup type
2. Entry price, stop, target, exit price
3. Outcome (win/loss/breakeven), R-multiple
4. Market condition (trending/ranging/volatile)
5. TICK reading at entry, VIX level
6. Emotion tag (calm/FOMO/fear/greedy/revenge)
7. Plan adherence (yes/no + reason if no)
8. Screenshot of chart at entry

### Review Schedule
| Frequency | Action | Time |
|-----------|--------|------|
| Post-trade | 60-second voice memo | 1 min |
| Daily | Review all trades, note patterns | 15 min |
| Weekly | Calculate metrics by setup type | 30 min |
| Monthly | Deep review, strategy audit | 2 hours |
| Quarterly | Strategy R&D pipeline update | 4 hours |

### Journaling Tools
- **Edgewonk**: $169 one-time, comprehensive analytics
- **TraderSync**: $29/mo, cloud-based, good UI
- **TradeZella**: Modern, mobile-friendly
- **Spreadsheet**: Free, customizable, requires discipline

## Personal Playbook Builder

### Edge-Defining Setups (Document These)
For each setup you trade, write:
1. **Market Context Required**: ADX range, VIX level, time of day
2. **Setup Criteria**: Exact conditions that must be present
3. **Entry Trigger**: The specific action that causes entry
4. **Stop Placement**: Exact location and reasoning
5. **Target Management**: TP1, TP2, trailing rules
6. **Max Risk**: Dollar amount and contract count
7. **When to Skip**: Conditions that invalidate the setup
8. **Performance History**: WR, PF, expectancy from your data

**Rule**: If you cannot write the setup rules on one page, you do not truly know the setup.

## Reference: Deep Research

For walk-forward methodology, Monte Carlo details, academic studies on strategy decay, and optimization dangers, see `references/backtest-deep-research.md`.
