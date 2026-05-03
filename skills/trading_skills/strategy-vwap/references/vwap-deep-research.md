# VWAP Deep Research Reference

## Statistical Foundation

The Volume Weighted Average Price (VWAP) is the average price weighted by volume, resetting at the beginning of each session. Price tends to revert to VWAP because it represents where the majority of volume has transacted — the market's center of gravity.

Adding standard deviation bands around VWAP normalizes volatility across instruments:
- SPY at $431 and COP at $34 can be analyzed through the same lens using VWAP ±2σ bands.
- Standard deviations succeed where dollar and percent measurements cannot.

## Backtest Results

### QuantifiedStrategies VWAP Study

5-day VWAP mean reversion on SPY:
- **CAGR**: 8.18% vs. 2.67% for 100-day trend-following approach
- **Principle**: Short-term mean reversion outperforms on short lookbacks
- **Time in market**: Substantially lower than buy-and-hold

### Trader-Documented MNQ VWAP Mean Reversion

Rules from verified futures trader:
1. Wait for price to stretch into VWAP standard deviation bands
2. Look for a return toward the first deviation
3. Enter on a close between the inner deviation and VWAP
4. Exit at VWAP or key psychological/support-resistance level

Results: 50-75 points consistently, 100+ on stronger days. Best after 10:30 AM once directional move has played out.

### Academic/Practitioner Consensus

- VWAP is widely used by institutions as benchmark → creates self-reinforcing reversion behavior
- 5-day VWAP: mean reversion dominates
- 100-day+ VWAP: trend-following dominates
- Intraday VWAP: hybrid — reversion in morning, continuation after establishment

## Volatility Regime Adaptation

A sophisticated approach classifies session into regimes:
- **Range regime**: Signals trigger at ±2σ band touches for mean reversion
- **Trend regime**: Mean reversion suppressed; only continuation signals at VWAP retests
- **Chop regime**: All signals suppressed to avoid whipsaw

Regime classification uses realized volatility vs. ATR and VWAP cross count.

## Conflict Zones

1. **VWAP mean reversion fails in strong trends**: Must filter with ADX. No filter = disaster.
2. **First 15 minutes unreliable**: Opening volume anchors VWAP but it moves too fast for reliable signals.
3. **±2σ assumption not always normal**: Fat tails during events make ±2σ less reliable. Monitor VIX.
4. **Micro vs Mini contract VWAP**: Same principles, but micros allow finer position sizing at bands.

## Key Sources

- TheVWAP.com — Standard deviation normalization across instruments
- QuantifiedStrategies — 5-day vs. 100-day VWAP backtest
- TrendSpider — VWAP StdDev bands documentation
- Bulls on Wall Street — Afternoon VWAP reliability
