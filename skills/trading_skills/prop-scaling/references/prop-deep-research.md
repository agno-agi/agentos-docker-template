# Prop Firm Deep Research Reference

## Detailed Firm Comparison

### Profit Split Comparison
| Firm | First $ | After First | Payout Frequency | Min Days to Payout |
|------|---------|-------------|------------------|-------------------|
| Apex | 100% first $25K | 90/10 | After 8 days, 5 profitable days $50+ | 8 |
| MFFU Scale/Pro | 100% first $10K | 90/10 | Every 5 winning days | 5 |
| Topstep | 100% first $10K | 90/10 | After consistency met | Varies |
| Earn2Trade | 80/20 | 80/20 | Monthly | 10 |

### Drawdown Mechanics Detail

**EOD Trailing Drawdown (MFFU, Topstep, Earn2Trade)**
- Drawdown trails your END-OF-DAY equity high
- Intraday dips do NOT affect drawdown
- Example: $50K account, $2K EOD drawdown
  - Day 1: Close at $51K → drawdown trails to $49K
  - Day 2: You can drop to $49K intraday without breach
  - Day 2: Close at $52K → drawdown trails to $50K

**Intraday Trailing Drawdown (Apex)**
- Drawdown follows your INTRADAY equity peak
- Never resets downward
- Example: $50K account, $2.5K trailing
  - Peak at $51K → drawdown = $48.5K
  - Even if you close at $50K, drawdown stays at $48.5K
  - One big pullback can breach drawdown even if still in profit

## Consistency Rule Math

### MFFU Consistency Rule
- No single trading day can account for >50% of total profits during evaluation
- Example: $3,000 profit target
  - Day 1: $1,600 → 53% of total → VIOLATION if you stop
  - Must continue trading until other days dilute the percentage
  - Target: $400-500/day average

### Topstep Consistency Rule
- Similar percentage-based rule
- Also: no single day can lose >50% of total drawdown
- Multiple violations = account review

### Apex — No Consistency Rule
- Apex does NOT have a consistency rule
- Advantage: one good day can pass the eval
- Risk: encourages gambling behavior

## Account Stacking Limits (Verified)
| Firm | Max Accounts | Stacking Allowed | Copier Allowed |
|------|-------------|------------------|----------------|
| Apex | 20 | Yes | Yes |
| MFFU | 10 (5 sim-funded active) | Yes | Yes |
| Topstep | 5 | Yes | Yes |
| Earn2Trade | 3 | Yes | Yes |
| Bulenox | 3 | Yes | Yes |

## Industry Pass Rates
- Earn2Trade reports: 8.89% pass rate (publicly disclosed)
- Industry estimate: 8-20% across all firms
- Traders with structured risk management: significantly higher

## Business Model Sustainability Questions

### The Prop Firm Math
- Firm collects evaluation fees (~$50-500 per eval)
- 80-90% of traders fail eval
- Successful traders funded with firm's capital
- Firm keeps 10-20% of trader profits
- Risk: if too many traders succeed simultaneously, firm is exposed

### Conflict Zone
- Some firms have been accused of tightening rules post-funding
- Payout delays reported by some traders
- Solution: diversify across 2-3 firms, not all-in on one

## Technology for Scaling

### VPS Requirements by Scale Phase
| Phase | Accounts | VPS Spec | Latency Requirement |
|-------|----------|----------|---------------------|
| 1-3 | 1-3 | Basic ($20/mo) | <50ms acceptable |
| 4-8 | 4-8 | Standard ($40/mo) | <20ms preferred |
| 9-20 | 9-20 | Premium ($80/mo) | <10ms required |

### Risk Aggregation
- Never risk >1% per trade across ALL accounts combined
- Example: 10 accounts × $50K = $500K total
- 1% risk = $5,000 maximum exposure on single trade idea
- Spread risk across uncorrelated setups
