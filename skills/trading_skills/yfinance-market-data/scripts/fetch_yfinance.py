#!/usr/bin/env python3
"""Fetch timestamped market data from yfinance as stable JSON."""

from __future__ import annotations

import argparse
import json
import math
from datetime import UTC, datetime
from typing import Any

import yfinance as yf  # type: ignore[reportMissingImports]


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def epoch_to_iso(value: Any) -> str | None:
    if value in (None, ""):
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=UTC).isoformat()
    except (TypeError, ValueError, OSError):
        return None


def json_value(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, float) and math.isnan(value):
        return None
    if hasattr(value, "item"):
        return json_value(value.item())
    return value


def get_mapping_value(mapping: Any, key: str) -> Any:
    if mapping is None:
        return None
    try:
        return mapping[key]
    except (KeyError, TypeError):
        return None


def last_index_timestamp(history: Any) -> str | None:
    if history is None or history.empty:
        return None
    value = history.index[-1]
    if hasattr(value, "to_pydatetime"):
        value = value.to_pydatetime()
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def build_history_rows(history: Any, rows: int) -> list[dict[str, Any]]:
    if history is None or history.empty:
        return []

    selected = history.tail(rows)
    output: list[dict[str, Any]] = []
    for index, row in selected.iterrows():
        timestamp = index.to_pydatetime() if hasattr(index, "to_pydatetime") else index
        if isinstance(timestamp, datetime):
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=UTC)
            timestamp_value = timestamp.astimezone(UTC).isoformat()
        elif hasattr(timestamp, "isoformat"):
            timestamp_value = timestamp.isoformat()
        else:
            timestamp_value = str(timestamp)

        output.append(
            {
                "timestamp": timestamp_value,
                "open": json_value(row.get("Open")),
                "high": json_value(row.get("High")),
                "low": json_value(row.get("Low")),
                "close": json_value(row.get("Close")),
                "volume": json_value(row.get("Volume")),
            }
        )
    return output


def build_quote_summary(ticker: Any, history: Any) -> dict[str, Any]:
    fast_info = getattr(ticker, "fast_info", None)
    info = {}
    try:
        info = ticker.info or {}
    except Exception:
        info = {}

    return {
        "price": json_value(get_mapping_value(fast_info, "last_price") or info.get("regularMarketPrice")),
        "previous_close": json_value(
            get_mapping_value(fast_info, "previous_close") or info.get("regularMarketPreviousClose")
        ),
        "open": json_value(get_mapping_value(fast_info, "open") or info.get("regularMarketOpen")),
        "day_high": json_value(get_mapping_value(fast_info, "day_high") or info.get("regularMarketDayHigh")),
        "day_low": json_value(get_mapping_value(fast_info, "day_low") or info.get("regularMarketDayLow")),
        "volume": json_value(get_mapping_value(fast_info, "last_volume") or info.get("regularMarketVolume")),
        "average_volume": json_value(get_mapping_value(fast_info, "ten_day_average_volume") or info.get("averageVolume")),
        "market_cap": json_value(get_mapping_value(fast_info, "market_cap") or info.get("marketCap")),
        "currency": json_value(get_mapping_value(fast_info, "currency") or info.get("currency")),
        "exchange": json_value(get_mapping_value(fast_info, "exchange") or info.get("exchange")),
        "latest_bar": last_index_timestamp(history),
    }


def choose_last_updated(ticker: Any, history: Any) -> str | None:
    metadata = getattr(ticker, "history_metadata", {}) or {}
    info = {}
    try:
        info = ticker.info or {}
    except Exception:
        info = {}

    return (
        epoch_to_iso(metadata.get("regularMarketTime"))
        or epoch_to_iso(info.get("regularMarketTime"))
        or last_index_timestamp(history)
    )


def fetch_market_data(ticker_symbol: str, mode: str, period: str, interval: str, rows: int) -> dict[str, Any]:
    normalized_ticker = ticker_symbol.strip().upper()
    retrieved_at = utc_now()

    try:
        ticker = yf.Ticker(normalized_ticker)
        history = ticker.history(period=period, interval=interval, auto_adjust=False)
        quote = build_quote_summary(ticker, history)
        result: dict[str, Any] = {
            "source": "yfinance",
            "ticker": normalized_ticker,
            "mode": mode,
            "retrieved_at": retrieved_at,
            "last_updated": choose_last_updated(ticker, history),
            "quote": quote,
        }

        if mode == "detailed":
            result["history"] = {
                "period": period,
                "interval": interval,
                "rows_returned": min(rows, len(history.index)) if history is not None else 0,
                "ohlcv": build_history_rows(history, rows),
            }

        if not quote.get("price") and (history is None or history.empty):
            result["warning"] = "yfinance returned no price or history data for this ticker."

        return result
    except Exception as exc:
        return {
            "source": "yfinance",
            "ticker": normalized_ticker,
            "mode": mode,
            "retrieved_at": retrieved_at,
            "last_updated": None,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch yfinance market data as JSON.")
    parser.add_argument("--ticker", required=True, help="Yahoo Finance-compatible ticker, e.g. AAPL or SPY.")
    parser.add_argument("--mode", choices=("basic", "detailed"), default="basic")
    parser.add_argument("--period", default="5d", help="yfinance history period, e.g. 1d, 5d, 1mo, 1y.")
    parser.add_argument("--interval", default="1d", help="yfinance history interval, e.g. 1m, 5m, 1h, 1d.")
    parser.add_argument("--rows", type=int, default=5, help="Number of OHLCV rows to return in detailed mode.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = max(args.rows, 0)
    result = fetch_market_data(args.ticker, args.mode, args.period, args.interval, rows)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
