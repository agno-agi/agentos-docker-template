# Market Internals Deep Research Reference

## Institutional Weighted Scoring Model

Some professional traders use a weighted composite:
- VOLD (Up Volume / Down Volume): 50% weight
- NYSE ADD: 30% weight
- NYSE TICK: 20% weight

| Composite Score | Market Condition | Trading Posture |
|-----------------|------------------|-----------------|
| > +60 | Strong trending | Aggressive, size up |
| +20 to +60 | Moderate trending | Normal operation |
| -20 to +20 | Mixed/choppy | Defensive, reduce size |
| -20 to -60 | Moderate weakness | Only counter-trend at extremes |
| < -60 | Severe weakness | Flat or fade only |

## TICK Advanced Patterns

### TICK "Ticks to Zero" Scalping
- Wait for TICK to spike to extreme (±800)
- Fade the move as TICK returns toward zero
- 2-4 point scalps on ES
- Requires fast execution; best in first hour

### TICK Divergence at Extremes
- Price at new high, TICK at lower high = classic divergence
- Highest probability when TICK < +500 on new price high
- Wait for 1-min reversal candle before entry

## VIX Term Structure

VIX futures curve shape predicts volatility regime:
- **Contango** (VIX < front-month futures): 84% of time. Normal. Expect gradual vol decline.
- **Backwardation** (VIX > front-month futures): 16% of time. Crisis/stress. Expect elevated vol.
- Academic research (Whaley, 2000): VIX term structure strategies produce double-digit Sharpe ratios.

## TRIN (Arms Index)

TRIN = (Advancing Issues / Declining Issues) / (Up Volume / Down Volume)

| TRIN Reading | Interpretation |
|-------------|----------------|
| < 0.50 | Severely overbought |
| 0.50-0.80 | Overbought |
| 0.80-1.00 | Mildly bullish |
| 1.00 | Neutral |
| 1.00-1.20 | Mildly bearish |
| 1.20-2.00 | Oversold |
| > 2.00 | Severely oversold |

**Key Signal**: TRIN divergence from price. TRIN rising while price rising = volume not confirming.

## Conflict Zones

1. **TICK Extreme Reliability**: TICK ±1000 exhaustion works best in first hour. Less reliable midday.
2. **VIX Directional vs Non-Directional**: VIX measures expected vol, not direction. Rising VIX can accompany rising OR falling prices.
3. **ADD Lag**: NYSE ADD is slower than TICK. Best for 5-min+ decisions, not scalping.
4. **Internals vs Futures**: TICK/ADD are stock-based; futures may lead or lag. Use as confirmation, not gospel.
