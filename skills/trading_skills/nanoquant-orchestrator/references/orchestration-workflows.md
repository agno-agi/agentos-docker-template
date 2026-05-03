# Orchestration Workflows Reference

## Advanced Coordination Patterns

### Pattern: Multi-Strategy Portfolio Review
**When**: Monthly or quarterly strategy audit

**Workflow**:
1. Pull performance data from `backtest-analytics`
2. For each active strategy, load its skill:
   - ORB performance → `strategy-orb`
   - VWAP performance → `strategy-vwap`
   - Order flow → `strategy-orderflow`
3. Load `market-internals` — has market regime shifted?
4. Load `risk-psychology` — is psychology affecting metrics?
5. Synthesize: Which strategies to keep, modify, or retire?

**Output**: Strategy portfolio health dashboard

### Pattern: Prop Firm Eval Day
**When**: User is taking prop firm evaluation

**Workflow**:
1. Load `prop-scaling` — specific firm rules
2. Load `risk-psychology` — eval-specific risk (0.5% per trade)
3. Load `strategy-orb` or `strategy-vwap` — eval-optimized setup
4. Load `market-internals` — only take A+ setups
5. Monitor: Daily drawdown proximity, consistency rule compliance

**Output**: Eval-specific daily plan with firm constraint checks

### Pattern: Event Day Protocol
**When**: Tier 1 event scheduled (NFP, FOMC, CPI)

**Workflow**:
1. Load `event-driven` — specific playbook
2. Load `market-internals` — VIX regime check
3. Load `risk-psychology` — reduce size, wider stops
4. Load all strategy skills — modify rules for event day
5. Decision tree: pre-position / wait-for-reaction / avoid

**Output**: Event-specific trading plan with risk modifications

### Pattern: Recovery Protocol (After Drawdown)
**When**: User has hit drawdown or had a bad streak

**Workflow**:
1. Load `risk-psychology` — emotional regulation
2. Load `backtest-analytics` — verify strategy still has edge
3. Load `risk-psychology` (drawdown section) — size reduction rules
4. Load relevant strategy skills — any rules being violated?
5. Plan: Recovery timeline with graduated size increases

**Output**: Structured recovery plan with milestones

## Edge Case Handling

### Case: User Wants to Trade Counter-Trend
**Response**:
1. Check `market-internals` — is there TICK divergence?
2. Check `strategy-vwap` — is price at ±2σ band?
3. Check `risk-psychology` — is this FOMO or a real setup?
4. If ALL conditions met → allow with 50% size
5. If any condition missing → explain why counter-trend is dangerous

### Case: User Wants to Hold Through Event
**Response**:
1. Load `event-driven` — what event, what playbook says
2. Check `prop-scaling` — does firm allow it?
3. Default position: flat into Tier 1 events unless pre-positioning strategy active
4. If holding: require 2x stop width, 50% size

### Case: Multiple Setup Opportunities Simultaneously
**Response**:
1. Rank by setup quality (A > B > C)
2. Check correlation — are they the same trade idea?
3. If correlated → take only the highest quality one
4. If uncorrelated → can take both with reduced size each
5. Total risk across all setups ≤ 2% daily max

## Orchestration Anti-Patterns

### Never Do This:
- Recommend a strategy without checking risk limits first
- Analyze a setup without checking market internals
- Suggest increasing size after losses (revenge trading enabler)
- Provide conflicting signals from different skills without resolution
- Ignore the emotional state component

### Always Do This:
- Lead with the verdict (GO/CAUTION/SKIP) then explain
- Provide exact numbers (entry, stop, target, size, risk $)
- Include "if-then" contingencies
- Reference specific skill criteria that were met or violated
- End with a clear, single actionable instruction
