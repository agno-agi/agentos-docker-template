# ORB Deep Research Reference

## Original Methodology: Toby Crabel

The Opening Range Breakout was formalized by Toby Crabel in Stocks & Commodities Magazine (1988, V. 6:9). Core principles:

- The "stretch" = 10-day average of the difference between open and the closest extreme (high or low) for each day.
- Buy/sell stops placed at stretch distance above/below the opening range high/low.
- Whichever side is traded first indicates bias for next 2-3 hours.
- An open outside the previous day's high/low sets up an intraday upthrust or spring — 67% continuation rate on a move back into the prior day's range by two ticks.
- Time-based exits: if the trade doesn't move within 15-30 minutes, it's vulnerable.

## Backtest Results Summary

### QuantCrawler 1-Year Backtest (Feb 2024 - Feb 2025)

| Metric | MNQ (5 contracts) | MES (10 contracts) |
|--------|-------------------|-------------------|
| Profit | $43,000 | $33,000 |
| Win Rate | 56.17% | 59.48% |
| Profit Factor | 1.369 | 1.269 |
| Trades | 454 | 501 |
| Max Drawdown | $12,400 | $12,000 |

Settings: Opening range 9:30-9:45 AM ET, entry on 5-min candle body close outside zone, stop = opposite side of range, TP1 at 1.0R, TP2 at 1.5R. Commissions $1.50/contract, slippage 2 ticks.

### Optimized MNQ ORB (90 Days)

- Trade window: 9:45 AM - 11:00 AM ET only
- No Fridays
- Win rate: 68.75%
- Profit factor: 3.053
- Profit: $12,274

Caveat: Optimization on recent data may be curve-fit. Use walk-forward validation before deploying.

### Option Alpha 0DTE ORB (SPX)

| OR Window | Win Rate | Profit Factor | Avg P/L | Max DD |
|-----------|----------|---------------|---------|--------|
| 60-min | 89.4% | 1.44 | $39 | $3,453 |
| 30-min | 82.6% | 1.38 | $35 | $3,891 |
| 15-min | 78.1% | 1.31 | $31 | $4,210 |

Wider OR windows produce higher win rates by filtering more noise.

## Key Filters That Improve Performance

1. **RVOL > 1.5**: Relative volume expansion confirms breakout has participation.
2. **VIX < 30**: Avoid high-volatility chop regimes.
3. **ADD Confirmation**: Breakout direction aligns with NYSE breadth.
4. **NR7 Prior Day**: Volatility contraction precedes expansion (Crabel's principle).
5. **No Major Economic Release**: Avoid 30 minutes post-NFP/FOMC/CPI.
6. **Friday Filter**: Backtest and exclude if Fridays underperform.

## ORB Failure Patterns

- **False Breakout**: Price breaks OR, reverses within 2-3 candles. Antidote: require body close outside range, not just wick.
- **No Volume**: Breakout on low RVOL (< 1.2) fails ~65% of the time.
- **Midday ORB**: ORB after 11 AM has significantly lower win rate.
- **Opposing Daily Structure**: If daily chart shows major support/resistance at OR level, breakout likely stalls.

## Conflict Zone: ORB Degradation

- Unfiltered ORB performance varies significantly year-to-year.
- As algorithmic participation increases, opening range edges may decay.
- Countermeasure: combine with order flow confirmation (footprint delta) for validation.
