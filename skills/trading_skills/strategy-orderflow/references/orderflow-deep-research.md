# Order Flow Deep Research Reference

## Platform-Specific Tools

### NinjaTrader Order Flow+
- Bid×Ask, Delta, and Volume footprint types
- Imbalance detection with customizable thresholds
- Auto-refresh at tick-level granularity

### Sierra Chart Numbers Bars
- Fastest C++ implementation
- DOM integration with 20+ depth levels
- Custom study overlays

### Bookmap
- Heatmap visualization of historical order flow
- Institutional level highlighting
- Best for learning, not execution

### ATAS
- 400+ footprint variations
- Volume profile + order flow combo
- $70/mo Pro tier

### Jigsaw Trading
- Pure DOM-focused platform
- $197/mo
- Best for dedicated DOM scalpers

## Academic Microstructure Foundations

### CME Matching Engine
- 70.3% FIFO (First In First Out) allocation
- Remainder pro-rata
- Understanding matching helps predict fill quality

### Cont, Stoikov & Talreja (2014)
- Order flow toxicity predicts short-term price direction
- VPIN (Volume-synchronized Probability of Informed Trading)
- High order flow toxicity → increased volatility

## Detailed Pattern Library

### Footprint Pattern: Imbalance Stacking at VAH
1. Price approaches Value Area High
2. Footprint shows consecutive ask imbalances at 3+ price levels
3. Delta rises sharply
4. Volume expands
→ **Signal**: Breakout continuation with high probability

### Footprint Pattern: Absorption at POC
1. Price returns to Point of Control
2. Footprint shows massive volume at POC
3. Price barely moves despite heavy volume
4. Delta neutral or diverging
→ **Signal**: Exhaustion at fair value → fade the direction

### Tape Pattern: Large Lot Trap
1. Tape shows 1000+ contract prints going through
2. Price does NOT move in direction of prints
3. Level holds despite repeated hits
→ **Signal**: Large player absorbing = imminent reversal

## Conflict Zones

1. **DOM vs. HFT**: Retail DOM refresh is 100-500ms; HFT reacts in <1ms. Retail edge is PATTERN RECOGNITION, not speed.
2. **CVD Divergence Reliability**: Best as context, not standalone trigger. Requires price confirmation.
3. **POC Win Rate Claims**: 65-70% is validated for pullbacks; degrades significantly when VIX > 40.
4. **87%+ Win Rate Claims**: Vendor marketing for footprint patterns. Independent testing shows 60-70%.
