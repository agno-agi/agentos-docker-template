# Risk & Psychology Deep Research Reference

## Cost of Trading Math

### Break-Even Win Rate Formula
```
Break-Even WR% = (Cost per Trade) / (Average Win + Average Loss) × 100
```

For a scalper on MES:
- Average win: 4 ticks ($5)
- Average loss: 4 ticks ($5)
- Round-trip commission: $1.24 (Tradovate) + $0.02 NFA + exchange fees
- Break-even: 55% just to cover commissions at 1:1 R:R

### Micro vs Mini Commission Drag
| Contract | Commission | 5-Tick Target Cost % |
|----------|-----------|---------------------|
| MES (micro) | ~$1.24 RT | ~18% of target |
| ES (mini) | ~$2.50 RT | ~5.7% of target |

Conclusion: Use mini contracts once account supports them. Micros are for learning, not long-term profit.

## Position Sizing Methods

### Fixed Fractional (1% Rule)
- Most widely used by professionals
- Produces smoother equity curves (Balsara, 1992)
- Formula: Risk$ / (Entry - Stop) = Share/Contract Count

### Kelly Criterion
```
f = (bp - q) / b
```
- f = fraction of capital to risk
- b = win/loss ratio
- p = probability of win
- q = probability of loss

**Critical**: No professional uses "full Kelly." Half-Kelly or quarter-Kelly maximum.

### Fixed Ratio (Ryan Jones)
- Increase size after gaining predetermined "delta" amount
- Slower growth but protects during drawdowns
- Formula: Units = √(Account / (2 × Delta))

### ATR-Based Sizing
- Position size proportional to volatility
- Larger stops in high ATR = fewer contracts
- Smaller stops in low ATR = more contracts
- Maintains constant dollar risk across market conditions

## Drawdown Protocol

### Three-Tier System
| Drawdown | Size Adjustment | Daily Limit |
|----------|----------------|-------------|
| 0-3% | 100% normal | 3% |
| 3-5% | 50% normal | 2% |
| 5-10% | 25% normal | 1% |
| >10% | STOP. Re-evaluate strategy | 0% |

### Recovery Timeline
- 3% drawdown: ~1 week at normal performance
- 5% drawdown: ~2-3 weeks with reduced size
- 10% drawdown: ~1-2 months with disciplined recovery
- 20% drawdown: ~3-6 months (if recoverable)

## Academic Psychology Findings

### Barber & Odean (Journal of Finance, 2000)
- 66,465 household accounts studied
- Most active traders underperformed by 6.5% annually
- Active trading households: 11.4% return vs. 17.9% market

### Kahneman & Tversky (Prospect Theory)
- Losses felt ~2x as intensely as equivalent gains
- Creates systematic risk aversion for gains, risk-seeking for losses

### Odean (1998) — Disposition Effect
- Traders 1.5x more likely to sell winners than losers
- Reduces annual returns by 3-5%
- Mindfulness training reduces this effect by 28%

### Prasad et al. (2025)
- Mindfulness reduces cortisol, increases testosterone
- Improves trading performance through emotional regulation
- **Caveat**: Ding et al. (2025) found mindfulness IMPAIRS performance in high-information-load scenarios (-35.4%)

## Revenge Trading Data

From analysis of 72 revenge trades:
- 68/72 followed a losing trade directly
- 4/72 followed breakeven trades (felt like losses)
- 0/72 followed winning trades
- Average time between loss and revenge entry: 8 minutes
- Fastest: 90 seconds
- Revenge position size: 1.4x normal average, 2-3x on bad days
- Revenge trade expectancy: -0.3 R vs. +0.4 R on plan-adherent trades

## Plan Adherence Correlation

| Adherence Rate | Likely Outcome |
|----------------|---------------|
| <60% | Almost certainly losing money |
| 60-75% | Breakeven to small loss |
| 75-85% | Small profit possible |
| 85-95% | Consistent profitability |
| >95% | Professional-grade performance |
