---
name: yfinance-market-data
description: >
  Fetches stock and ETF market data with yfinance for NanoQuant agents. Use when
  the user asks for a stock quote, current market data, OHLCV history, price
  action, volume, market cap, or a timestamped yfinance data snapshot.
---

# YFinance Market Data

Use this skill when a NanoQuant agent needs market data for a requested stock,
ETF, or Yahoo Finance-compatible symbol.

## Data Modes

- `basic`: quote summary for the requested symbol.
- `detailed`: quote summary plus OHLCV history.

Every response must include:

- `retrieved_at`: when NanoQuant fetched the data.
- `last_updated`: best available update timestamp from yfinance metadata or the
  latest returned price bar.
- `source`: `yfinance`.
- `ticker`: normalized uppercase ticker.

## Utility Script

Run the script from the project root:

```bash
python skills/yfinance-market-data/scripts/fetch_yfinance.py --ticker AAPL --mode basic
python skills/yfinance-market-data/scripts/fetch_yfinance.py --ticker TSLA --mode detailed --period 5d --interval 1d --rows 5
```

## Output Guidance

For user-facing answers:

1. State the ticker and data mode used.
2. Include the `last_updated` timestamp.
3. Summarize key fields instead of dumping raw JSON unless the user asks for raw data.
4. Mention if yfinance returned partial or unavailable data.
