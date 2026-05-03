# Backtesting & Analytics Deep Research Reference

## Academic Findings on Strategy Performance

### Barber & Odean (Journal of Finance, 2000)
- 80% of active day traders lose money over 2 years
- Only ~1% earn consistent profits net of fees
- The 1% differentiate through discipline, not superior strategies

### Strategy Failure Rate (2014 Academic Study)
- 44% of published trading strategies fail when applied to new data
- Curve-fitting is the primary cause
- Countermeasure: walk-forward analysis with WFE > 50%

### Drawdown Recovery Asymmetry (Bailey & Lopez de Prado, 2014)
- Recovery typically takes 2-3x the drawdown formation period
- 50% loss requires 100% gain to recover (not 50%)
- Recovery math is non-linear; protect capital above all

## Walk-Forward Analysis Detail

### Standard Implementation
1. Divide data into N periods (e.g., 12 months)
2. For each period:
   a. Optimize parameters on previous M periods (in-sample)
   b. Test optimized parameters on current period (out-of-sample)
   c. Record out-of-sample performance
3. Aggregate out-of-sample results
4. Calculate Walk-Forward Efficiency (WFE):
   ```
   WFE = (Out-of-Sample Profit / In-Sample Profit) × 100%
   ```
5. **WFE > 50-60%**: Strategy is likely robust
6. **WFE < 50%**: Strategy is likely overfit

### Critical Warning
LuxAlgo research: "After testing just seven strategy configurations, a trader may find a 2-year backtest with an annualized Sharpe ratio above 1 even if the actual out-of-sample Sharpe ratio is zero."

## Monte Carlo Methodology

### Primary Methods
1. **Trade Scrambling**: Randomly reshuffle trade order 5,000+ times
2. **Equity Curve Scrambling**: Assemble random portions of equity curve
3. **Block Bootstrap**: Preserve autocorrelation with blocks of ~10 trades

### Key Parameters
- **Minimum simulations**: 5,000 for stable estimates; 10,000+ for tail risk
- **Path length**: Match intended investment horizon
- **Bootstrap rule**: Never bootstrap in-sample returns

### Example Output Interpretation
Backtest shows 8% max DD. Monte Carlo reveals:
- 50th percentile DD: 9%
- 75th percentile DD: 14%
- 90th percentile DD: 18%
- 95th percentile DD: 24%

**Action**: Size positions assuming 18% max DD (90th percentile), not 8%.

## Optimization Dangers

### The Parameter Explosion Problem
- More parameters = more ways to curve-fit
- Rule: Maximum 3-4 optimizable parameters per strategy
- Parameter stability test: vary each parameter ±20%, verify performance doesn't collapse

### In-Sample vs. Out-of-Sample Allocation
| Purpose | Allocation | Usage |
|---------|-----------|-------|
| In-Sample (Training) | 60-80% | Build and optimize strategy |
| Out-of-Sample (Validation) | 20-30% | Test untouched until final |
| Holdout (Test) | Optional 10% | Used exactly once at very end |

## Strategy Degradation Indicators

### Market Regime Changes
- ADX shifting from <20 to >25 or vice versa
- VIX sustained >30 or <12
- Correlation breakdown (e.g., ES/NQ correlation dropping from 0.95 to <0.80)
- CUSUM test or Kolmogorov-Smirnov test for distribution shifts

### Ray Dalio's Holy Grail
- 15 uncorrelated return streams can reduce risk by 80% without reducing return
- Application: maintain 3-5 uncorrelated strategies
- When one degrades, others continue producing

## Key Sources

- LuxAlgo Blog — Walk-forward and in-sample/out-of-sample testing
- EdgeFlo — One-month testing protocol before live
- QuantVPS — Algorithmic trading prevalence and forward testing
- Curtis Faith "Way of the Turtle" — System design principles
