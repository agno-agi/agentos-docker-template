---
name: nanoquant-stockfit
description: >
  Stockfit screener and signals fetching for the NanoQuant trading agent. Use this skill
  whenever NanoQuant needs to pull screener results, technical signals, trade alerts, or
  any scan data from the Stockfit API. Triggers on: "run a screener", "get signals for",
  "what's screening", "stockfit scan", "pull alerts", "technical signals", "screener results",
  or any request for Stockfit data before storing. This is step 2 of the NanoQuant pipeline —
  always run after nanoquant-alpaca and before nanoquant-duckdb.
---

# NanoQuant — Stockfit MCP Skill

Fetch screener results and trading signals from Stockfit via the `stockfit-api` MCP server. This is **step 2** of the NanoQuant pipeline. After fetching, hand off to `nanoquant-duckdb` to store.

## MCP Server: `stockfit-api`

The `stockfit-api` MCP server connects to `https://api.stockfit.io/mcp` using a Bearer token. Authentication is handled automatically via the OpenClaw config — no additional setup needed.

---

## Tool Discovery

Because Stockfit's MCP tool set may evolve, always begin a session by listing available tools if you haven't used this server recently:

```
List tools from MCP server: stockfit-api
```

This returns the current set of tools, their parameters, and descriptions. Use that output as the authoritative reference for the session.

---

## Known Tool Patterns

Stockfit is a screener and signals platform. Its MCP tools typically follow these patterns:

### Screener / Scan Tools
Run a scan against the market to find symbols matching criteria (momentum, breakouts, volume surges, gap plays, etc.).

**Common parameters to expect:**
```
filters     object     Screening criteria (e.g. volume > 1M, RSI < 30, price > 5)
universe    string     Scope: "sp500", "nasdaq100", "russell2000", "all_us_equity"
limit       integer    Max results to return
```

**Returns:** Array of matching symbols with their signal metadata, scores, or indicator values.

### Signal / Alert Tools
Fetch signals or alerts for specific symbols you're already watching.

**Common parameters to expect:**
```
symbols     string[]   Ticker symbols to check
timeframe   string     Signal timeframe: "1D", "1W", "intraday"
signal_type string     e.g. "breakout", "reversal", "momentum", "mean_reversion"
```

**Returns:** Per-symbol signal objects with strength, direction, and supporting indicator values.

### Historical Signals
Fetch past signal history for backtesting or reviewing what Stockfit flagged on prior dates.

**Common parameters to expect:**
```
symbols     string[]   Ticker symbols
start       string     ISO 8601 start date
end         string     ISO 8601 end date
```

---

## How to Use Unknown Tools

When you discover a tool from the `list tools` call that isn't documented above:

1. Read its description and parameter schema carefully
2. Map its parameters to your intent (symbols, dates, filters)
3. Call it and inspect the response structure before storing
4. Note the field names in the response — you'll need them to store in DuckDB

---

## Pipeline Pattern

This skill is **step 2** of the NanoQuant data pipeline:

```
[nanoquant-alpaca] → fetch bars + news
         ↓
[nanoquant-stockfit] → fetch signals for same symbols   ← YOU ARE HERE
         ↓
[nanoquant-duckdb] → store all results
```

**Coordinate with Alpaca output:** Use the same symbol list that was passed to `get-stock-bars` in step 1. This keeps the DuckDB tables aligned by symbol and date.

---

## Common Workflows

**Daily signal pull:**
1. Take the watchlist symbols from the Alpaca step
2. Call the signal/screener tool for today's signals
3. Hand raw response to `nanoquant-duckdb` → `stockfit_signals` table

**Screener-first workflow:**
1. Run a screener scan to discover symbols (e.g. top momentum names)
2. Feed those symbols back to `nanoquant-alpaca` to fetch bars
3. Store everything in DuckDB

**Error handling:**
If the MCP server is unreachable or returns an error, log it and continue the pipeline with Alpaca data only. Stockfit signals are supplementary — do not block the pipeline on them.
