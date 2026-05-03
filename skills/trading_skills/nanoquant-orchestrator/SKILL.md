---
name: nanoquant-orchestrator
description: >
  Master orchestrator for NanoQuant backtesting and paper trading operations. Coordinates
  all trading skills, MCP data sources (Alpaca, Stockfit), and DuckDB storage to run
  systematic strategy tests on AAPL, GOOGL, and MSFT — one strategy at a time — before going live.
  Use when: (1) starting a backtest or paper trade session, (2) running a specific strategy
  (ORB, VWAP, orderflow) against target stocks, (3) reviewing backtest results or paper trade
  performance, (4) comparing strategies to pick the best one, (5) asking "what's working",
  (6) pre-market prep for paper trading, (7) any cross-skill coordination involving data
  fetching, strategy analysis, and result storage. This is the top-level entry point —
  always start here.
---

# NanoQuant Orchestrator

Coordinate all NanoQuant skills, MCP servers, and data tools to run systematic strategy
testing on target stocks. The current objective is **backtesting and paper trading** —
studying efficiency and optimizing before going live.

> **Phase**: Pre-live · Backtest & Paper Trade
> **Target stocks**: AAPL (Apple), GOOGL (Google/Alphabet), MSFT (Microsoft)
> **Active strategy**: One at a time (see Strategy Rotation below)

---

## Skill Map

All 14 skills available to NanoQuant. Skill names match folder names exactly.

### Data Pipeline
| Skill | MCP Server | Purpose |
|-------|-----------|---------|
| `nanoquant-alpaca` | `alpaca-mcp` | Fetch OHLCV bars, news, market calendar from Alpaca |
| `nanoquant-stockfit` | `stockfit-api` | Fetch screener results and technical signals |
| `nanoquant-duckdb` | `duckdb` | Store and query all pipeline data |
| `nanoquant-duckdb-ui` | — | Launch browser UI, generate Plotly.js charts |
| `yfinance-market-data` | — | Quick quotes and OHLCV via yfinance (no API key needed) |

### Strategy Skills
| Skill | Focus |
|-------|-------|
| `strategy-orb` | Opening Range Breakout — entry rules, stop placement, targets for AAPL/GOOGL/MSFT |
| `strategy-vwap` | VWAP pullback and SD band mean reversion |
| `strategy-orderflow` | DOM reading, cumulative delta, footprint charts, tape reading |
| `event-driven` | NFP, FOMC, CPI, earnings impact on AAPL/GOOGL/MSFT |

### Analysis & Risk
| Skill | Focus |
|-------|-------|
| `backtest-analytics` | Walk-forward analysis, Monte Carlo, win rate, profit factor, Sharpe |
| `market-internals` | VIX regime, NYSE TICK, ADD, multi-timeframe context filters |
| `risk-psychology` | Position sizing (1% rule), daily loss limits, drawdown protocols, Big Four emotions |
| `prop-scaling` | Prop firm evaluation paths — for when we're ready to scale capital |

---

## Strategy Rotation — Test One at a Time

Test strategies in this order. Do not run two simultaneously — mixed signals corrupt the
performance record. Complete the full backtest + paper trade cycle before moving to the next.

```
[1] ORB  (Opening Range Breakout)   ← start here
[2] VWAP (VWAP Pullback / SD Bands)
[3] Order Flow (DOM + Delta)
[4] Event-Driven (earnings / macro)
```

Current active strategy is noted in each session. When switching strategies, archive
results in DuckDB (`trade_log.strategy` field) so comparisons remain clean.

---

## Core Workflows

### Workflow 1: Run a Backtest

**Trigger**: "Backtest ORB on AAPL" / "Run a backtest" / "How did VWAP perform last quarter?"

**Steps:**
1. **Load `nanoquant-alpaca`** — fetch historical OHLCV bars
   - Symbols: `["AAPL", "GOOGL", "MSFT"]` (or one at a time)
   - Timeframe: match strategy (`"5Min"` for ORB/orderflow, `"1Day"` for swing context)
   - Range: minimum 6 months; 2 years preferred for walk-forward
   - Run `normalize_alpaca.py` → `bulk_insert.py` for large date ranges

2. **Load `nanoquant-stockfit`** — fetch signals for the same period
   - Use same symbols and date range
   - Store raw signals in `stockfit_signals` via `nanoquant-duckdb`

3. **Load `nanoquant-duckdb`** — confirm data is stored
   ```sql
   SELECT symbol, timeframe, MIN(ts), MAX(ts), COUNT(*) FROM ohlcv_bars GROUP BY 1,2;
   ```

4. **Load active strategy skill** (e.g., `strategy-orb`) — apply entry/exit rules
   - Identify all qualifying setups in the data window
   - Apply exact entry trigger, stop, and target rules from the skill
   - Record each simulated trade in `trade_log` with `strategy = 'ORB'`

5. **Load `backtest-analytics`** — compute performance metrics
   - Win rate, profit factor, expectancy, Sharpe ratio
   - Walk-forward efficiency (WFE) — target >50%
   - Monte Carlo simulation — 5,000+ runs for drawdown distribution

6. **Load `market-internals`** — apply context filters
   - Re-run backtest excluding high-VIX days (>25), extreme TICK days
   - Compare filtered vs. unfiltered performance

7. **Generate charts** via `nanoquant-duckdb-ui`
   ```bash
   python chart_trading.py equity --strategy ORB
   python chart_trading.py returns --strategy ORB
   python chart_trading.py ohlcv --symbol AAPL --timeframe 5Min --days 30
   ```

**Output format:**
```
## Backtest Results — [Strategy] on [SYMBOLS]
### Period: [start] → [end] | Timeframe: [X]

### Performance
- Total trades:    [N]
- Win rate:        [X%]
- Profit factor:   [Y]
- Expectancy:      [$Z per trade]
- Sharpe ratio:    [W]
- Max drawdown:    [X%] (90th pct Monte Carlo: [Y%])
- WFE:             [Z%] → [Robust / Marginal / Overfit]

### Context Filter Impact
- Unfiltered:  [win rate, PF]
- VIX-filtered: [win rate, PF] → [improvement / degradation]

### Verdict: [PROCEED TO PAPER / MODIFY RULES / DISCARD]
```

---

### Workflow 2: Run a Paper Trade Session

**Trigger**: "Start paper trading ORB today" / "Paper trade session" / "Pre-market for paper trade"

**Pre-market (8:00–9:15 AM):**
1. **Load `market-internals`** — overnight context, VIX level, key levels
2. **Load `event-driven`** — check AAPL/GOOGL/MSFT earnings calendar, macro events
3. **Load active strategy skill** — review today's setup criteria and time windows
4. **Load `risk-psychology`** — confirm daily risk limit, emotional baseline
5. **Load `nanoquant-alpaca`** → `get-market-days` — confirm today is a trading day
6. **Fetch pre-market bars** → store in DuckDB for intraday reference

**During session:**
- Apply strategy rules from active strategy skill
- Each paper trade → log to `trade_log` immediately:
  ```sql
  INSERT INTO trade_log (symbol, side, entry_price, qty, entry_at, strategy, notes)
  VALUES ('AAPL', 'long', 195.40, 100, now(), 'ORB', 'ORB breakout above 9:35 high');
  ```
- After exit → update with `exit_price`, `exit_at`, `pnl`, `pnl_pct`

**Post-session review:**
1. Pull today's trades from DuckDB
2. Load `backtest-analytics` — add today's trades to rolling metrics
3. Load `risk-psychology` — emotional debrief
4. Run equity chart: `python chart_trading.py equity --strategy ORB`

**Output format:**
```
## Paper Trade Session — [Date] | Strategy: [X]

### Market Context
- VIX: [level] | Regime: [low/normal/high]
- Events: [any AAPL/GOOGL/MSFT news or macro]
- Bias: [long / short / neutral / skip]

### Trades
| # | Symbol | Side | Entry | Exit | P&L | Grade |
|---|--------|------|-------|------|-----|-------|
| 1 | AAPL   | Long | $195.40 | $197.20 | +$180 | B |

### Session P&L: [$X] | Win rate: [Y%] | Plan adherence: [Z%]
### Lesson: [one takeaway]
```

---

### Workflow 3: Strategy Comparison Review

**Trigger**: "Which strategy is performing best?" / "Compare ORB vs VWAP" / "Should I switch strategies?"

1. Query DuckDB for all strategy performance:
   ```sql
   SELECT strategy,
          COUNT(*)                                                   AS trades,
          ROUND(AVG(pnl), 2)                                        AS avg_pnl,
          ROUND(SUM(pnl), 2)                                        AS total_pnl,
          ROUND(SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END)
                ::FLOAT / COUNT(*) * 100, 1)                        AS win_rate_pct,
          ROUND(SUM(CASE WHEN pnl > 0 THEN pnl ELSE 0 END)
                / NULLIF(ABS(SUM(CASE WHEN pnl < 0 THEN pnl ELSE 0 END)), 0), 2) AS profit_factor
   FROM trade_log
   WHERE strategy IS NOT NULL
   GROUP BY strategy
   ORDER BY total_pnl DESC;
   ```

2. Load `backtest-analytics` — interpret results in context of sample size
3. Generate comparison charts via `nanoquant-duckdb-ui`
4. Recommend whether to continue current strategy, modify it, or rotate to next

**Minimum sample before declaring a winner**: 30+ trades per strategy per symbol.

---

### Workflow 4: Pre-Market Brief (Paper Trade Days)

**Trigger**: "What's the plan for today?" / "Pre-market analysis"

```
## Pre-Market Brief — [Date] | Paper Trading: [Strategy]

### Market Context
- VIX: [level] vs yesterday [delta] → Regime: [Low <15 / Normal 15-25 / High >25]
- Overnight: [high] / [low] / direction
- Key levels AAPL: [PDH, PDL, overnight H/L, major round numbers]
- Key levels GOOGL: [same]
- Key levels MSFT: [same]

### Events Today
- [Time]: [Event] — Impact: [Skip window / Trade with caution / Normal]
- AAPL/GOOGL/MSFT earnings: [date, expected move]

### Strategy Plan — [Active Strategy]
- Setup criteria reminder: [2-3 bullet summary from strategy skill]
- Time windows: [e.g., ORB = 9:30–10:30 AM, avoid 11-2 PM]
- Target R:R: [from strategy skill benchmarks]

### Risk Parameters
- Max risk per trade: [$X / Y shares]
- Daily paper loss limit: [$X]
- Contracts/shares: [size for paper account]

### Red Flags (skip today if any apply)
- [ ] VIX > 30
- [ ] AAPL, GOOGL, or MSFT earnings within 2 days
- [ ] Major macro event in first hour (FOMC, CPI, NFP)
- [ ] Gap > 1.5% at open (ORB only)
```

---

### Workflow 5: Post-Trade Review

**Trigger**: User shares a completed paper trade result

1. **Load `risk-psychology`** — emotional audit
2. **Load active strategy skill** — grade execution against exact rules
3. Log to DuckDB if not already done
4. Update rolling metrics in `backtest-analytics`

```
## Trade Review — [SYMBOL] [Strategy] [Win/Loss]

### Execution Grade: [A/B/C/D]
- Entry: [early / on trigger / late / missed]
- Stop: [too tight / correct / too wide]
- Target: [hit / partial / exited early / stopped]
- Process adherence: [Yes / No — if No, what deviated]

### Lesson: [one sentence]
### DuckDB logged: [Yes / No]
```

---

## Orchestration Rules

**Rule 1 — Data before decisions.** Always pull fresh Alpaca bars before analysis. Stale data
produces unreliable signals. Use `nanoquant-alpaca` → `nanoquant-duckdb` before strategy work.

**Rule 2 — One strategy at a time.** Tag every trade with `strategy` in `trade_log`. Never
mix strategy rules mid-session. The `strategy` column is the primary performance filter.

**Rule 3 — Minimum sample discipline.** Load `backtest-analytics` before
declaring a strategy valid or invalid. 10 trades is noise. 30+ per symbol is the floor.

**Rule 4 — Context always.** Before any strategy analysis, load `market-internals`
for VIX regime. High-VIX environments change strategy behavior significantly — filter results
by regime before optimizing parameters.

**Rule 5 — Synthesize, don't list.** Don't relay what each skill says separately. Produce
one integrated recommendation: PROCEED / MODIFY / PAUSE / DISCARD.

**Rule 6 — Store everything.** Every paper trade, backtest trade, and session note goes into
DuckDB. The accumulated dataset is how we optimize before going live.

---

## Session State

Maintain this across a session — update after each trade:

```
SESSION STATE
├── Date:              [YYYY-MM-DD]
├── Phase:             [Backtest / Paper Trade]
├── Active strategy:   [ORB / VWAP / OrderFlow / EventDriven]
├── Target symbols:    [AAPL, GOOGL, MSFT]
├── Paper P&L today:   [$X]
├── Trades taken:      [N]
├── Plan adherence:    [X%]
├── VIX regime:        [Low / Normal / High]
├── Daily limit used:  [X% of limit]
└── Notes:             [anything unusual]
```

---

## Go-Live Criteria (Future Reference)

Before moving from paper to live trading on any strategy:
- [ ] 30+ paper trades logged in DuckDB for that strategy
- [ ] Win rate ≥ backtest expectation (within ±5%)
- [ ] Max drawdown ≤ backtest 90th percentile Monte Carlo estimate
- [ ] WFE > 50% confirmed
- [ ] Two consecutive profitable paper-trade weeks
- [ ] `risk-psychology` sign-off: emotional discipline rated consistent
