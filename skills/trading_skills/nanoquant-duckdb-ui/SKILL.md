---
name: nanoquant-duckdb-ui
description: >
  Launch the DuckDB official browser UI against the NanoQuant trading database, or generate
  trading charts and visuals from DuckDB data. Use this skill whenever the user wants to
  open DuckDB UI, browse trading data visually, explore the database in a browser, create
  charts from OHLCV bars or P&L data, visualize signals, or plot any data from the
  NanoQuant DuckDB. Triggers on: "open duckdb ui", "launch duckdb", "visualize", "chart",
  "plot", "show me a chart of", "open the database ui", "browse the trading db", "duckdb visuals".
---

# NanoQuant — DuckDB UI & Visuals

Two ways to explore NanoQuant data visually:
1. **Browser UI** — the official DuckDB web interface, full SQL editor + built-in charts
2. **Chart scripts** — Python-generated OHLCV, P&L, and signal charts saved as PNG/HTML

---

## 1. Launch the DuckDB Browser UI

The official DuckDB UI (`-ui` flag) runs a local web server and opens a full SQL workbench in your browser. Requires DuckDB v1.2+.

### Launch command

```bash
duckdb ~/.openclaw/duckdb/trading.db -ui
```

Or use the helper script (handles version check and port reporting):

```bash
python skills/trading_skills/nanoquant-duckdb-ui/scripts/launch_ui.py
python skills/trading_skills/nanoquant-duckdb-ui/scripts/launch_ui.py --db ~/custom/nanoquant.db
python skills/trading_skills/nanoquant-duckdb-ui/scripts/launch_ui.py --port 9999
```

### What the UI includes
- Full SQL editor with syntax highlighting and autocomplete
- Schema browser (tables, columns, types)
- Query result table with sorting and filtering
- **Built-in chart panel** — select a result column as X/Y and choose chart type (line, bar, scatter, area)
- Export results to CSV or Parquet

### Default URL
`http://localhost:4213` — opens automatically when launched

### Stop the UI
`Ctrl+C` in the terminal where you ran the command.

---

## 2. Generate Interactive Charts with Plotly.js

All charts are self-contained HTML files rendered with Plotly.js — fully interactive with zoom, pan, hover, and crosshair. No matplotlib, no static images. Each chart auto-opens in your browser on generation.

Only one install needed:
```bash
pip install plotly duckdb --break-system-packages
```

### Supported chart types

| Chart | Description | Features |
|-------|-------------|----------|
| `ohlcv` | Candlestick + volume + VWAP overlay | Zoom, crosshair, range select |
| `equity` | Cumulative P&L equity curve | Win/loss fill, trade markers, hover |
| `signals` | Signal strength + long/short count | Stacked bars, dual axis |
| `returns` | Returns distribution histogram | Win rate, mean line, P&L summary |

### Usage

```bash
# Candlestick chart for SPY, last 30 days
python skills/trading_skills/nanoquant-duckdb-ui/scripts/chart_trading.py \
  ohlcv --symbol SPY --timeframe 1Day --days 30

# 1-hour bars for ES, last 5 days
python chart_trading.py ohlcv --symbol ES --timeframe 1Hour --days 5

# Equity curve for all strategies
python chart_trading.py equity

# Equity curve for one strategy
python chart_trading.py equity --strategy ORB

# Signal strength chart for MES, last 60 days
python chart_trading.py signals --symbol MES --days 60

# Returns distribution for all trades
python chart_trading.py returns

# Custom output path
python chart_trading.py ohlcv --symbol SPY --timeframe 1Day --days 30 --output ~/Desktop/spy.html
```

### Output
All charts save to `~/.openclaw/charts/` by default and auto-open in the browser. They are fully self-contained HTML files (Plotly.js loaded from CDN) — shareable with no dependencies.

---

## DuckDB UI Built-in Charts (Quick Reference)

Once you have query results in the UI, click the **Chart** tab above the results pane:

1. Run any SQL query
2. Click "Chart" tab in the results panel
3. Select chart type: Line, Bar, Area, Scatter, Pie
4. Assign columns to X-axis and Y-axis
5. Optionally group by a column for multi-series

**Example queries to visualize in the UI:**

```sql
-- Daily close prices for charting
SELECT ts::DATE AS date, close FROM ohlcv_bars
WHERE symbol = 'SPY' AND timeframe = '1Day'
ORDER BY date;

-- Cumulative P&L over time
SELECT exit_at::DATE AS date, SUM(pnl) OVER (ORDER BY exit_at) AS cumulative_pnl
FROM trade_log ORDER BY exit_at;

-- Signal strength by date
SELECT signal_date, AVG(strength) AS avg_strength
FROM stockfit_signals GROUP BY signal_date ORDER BY signal_date;
```

---

## Troubleshooting

**`-ui flag not recognized`** — Update DuckDB to v1.2+:
```bash
brew upgrade duckdb
```

**Port already in use:**
```bash
python launch_ui.py --port 4214
```

**Charts show blank / no data:**
Run `python init_db.py --verify` to confirm tables have data. If empty, run the pipeline first.

**`plotly not found`:**
```bash
pip install plotly duckdb --break-system-packages
```
