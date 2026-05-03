#!/usr/bin/env python3
"""
Normalize raw Alpaca MCP responses into DuckDB-ready rows.

Handles field remapping for bars and news:
  Bars:  t→ts, o→open, h→high, l→low, c→close, v→volume, vw→vwap, n→trade_count
  News:  created_at→published_at, per-symbol expansion for multi-symbol articles

Usage:
  # Normalize bars from a JSON file
  python normalize_alpaca.py bars --input bars_response.json --timeframe 1Day

  # Normalize bars from stdin (pipe from MCP output)
  echo '{"bars": {"SPY": [...]}}' | python normalize_alpaca.py bars --timeframe 1Day

  # Normalize news from a JSON file
  python normalize_alpaca.py news --input news_response.json

  # Output as SQL INSERT statements instead of JSON
  python normalize_alpaca.py bars --input bars.json --timeframe 1Day --format sql

  # Write output to a file
  python normalize_alpaca.py bars --input bars.json --timeframe 1Day --output rows.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import UTC, datetime
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(value: Any) -> Any:
    """Return None for NaN/Inf floats; pass everything else through."""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def _iso(value: Any) -> str | None:
    """Coerce a timestamp string to ISO 8601 UTC. Returns None on failure."""
    if not value:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat()
    try:
        # Already a string — normalize to UTC if offset is present
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC).isoformat()
    except (ValueError, TypeError):
        return str(value)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


# ---------------------------------------------------------------------------
# Bars normalizer
# ---------------------------------------------------------------------------

def normalize_bars(raw: dict[str, Any], timeframe: str) -> list[dict[str, Any]]:
    """
    Convert Alpaca get-stock-bars response to ohlcv_bars rows.

    Alpaca field → DuckDB column:
      t  → ts           (timestamp)
      o  → open
      h  → high
      l  → low
      c  → close
      v  → volume
      vw → vwap
      n  → trade_count

    Args:
        raw:       The parsed JSON object returned by the alpaca-mcp get-stock-bars tool.
                   Expected shape: {"bars": {"SYMBOL": [bar, ...], ...}}
        timeframe: The timeframe string used in the request (e.g. "1Day", "5Min").

    Returns:
        List of row dicts matching the ohlcv_bars table schema.
    """
    bars_by_symbol: dict[str, list] = raw.get("bars", {})
    if not bars_by_symbol:
        return []

    rows: list[dict[str, Any]] = []
    inserted_at = _utc_now()

    for symbol, bar_list in bars_by_symbol.items():
        if not isinstance(bar_list, list):
            continue
        for bar in bar_list:
            rows.append({
                "symbol":      symbol.upper(),
                "timeframe":   timeframe,
                "ts":          _iso(bar.get("t")),
                "open":        _clean(bar.get("o")),
                "high":        _clean(bar.get("h")),
                "low":         _clean(bar.get("l")),
                "close":       _clean(bar.get("c")),
                "volume":      bar.get("v"),
                "vwap":        _clean(bar.get("vw")),
                "trade_count": bar.get("n"),
                "inserted_at": inserted_at,
            })

    return rows


# ---------------------------------------------------------------------------
# News normalizer
# ---------------------------------------------------------------------------

def normalize_news(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Convert Alpaca get-news response to news_sentiment rows.

    One article may cover multiple symbols — this expands to one row per symbol
    so that per-symbol queries against news_sentiment work correctly.

    Alpaca field → DuckDB column:
      id           → id
      symbols[i]   → symbol       (one row per symbol)
      headline     → headline
      summary      → summary
      content      → content
      author       → author
      source       → source
      url          → url
      created_at   → published_at

    Args:
        raw: List of article objects returned by alpaca-mcp get-news tool.

    Returns:
        List of row dicts matching the news_sentiment table schema.
    """
    if not isinstance(raw, list):
        # Handle wrapped response: {"news": [...]}
        raw = raw.get("news", []) if isinstance(raw, dict) else []

    rows: list[dict[str, Any]] = []
    inserted_at = _utc_now()

    seen: set[tuple] = set()  # deduplicate (id, symbol) pairs

    for article in raw:
        article_id  = article.get("id")
        headline    = article.get("headline")
        summary     = article.get("summary")
        content     = article.get("content")
        author      = article.get("author")
        source      = article.get("source")
        url         = article.get("url")
        published_at = _iso(article.get("created_at") or article.get("updated_at"))

        symbols = article.get("symbols") or []
        if not symbols:
            # Store with empty symbol if no symbol association
            symbols = [""]

        for symbol in symbols:
            key = (article_id, symbol)
            if key in seen:
                continue
            seen.add(key)

            rows.append({
                "id":           article_id,
                "symbol":       symbol.upper() if symbol else "",
                "headline":     headline,
                "summary":      summary,
                "content":      content,
                "author":       author,
                "source":       source,
                "url":          url,
                "published_at": published_at,
                "inserted_at":  inserted_at,
            })

    return rows


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def rows_to_json(rows: list[dict[str, Any]]) -> str:
    return json.dumps(rows, indent=2, default=str)


def rows_to_sql_bars(rows: list[dict[str, Any]]) -> str:
    """Generate INSERT OR IGNORE SQL for ohlcv_bars."""
    if not rows:
        return "-- No rows to insert"

    lines = [
        "INSERT OR IGNORE INTO ohlcv_bars",
        "  (symbol, timeframe, ts, open, high, low, close, volume, vwap, trade_count, inserted_at)",
        "VALUES"
    ]
    value_lines = []
    for r in rows:
        def q(v: Any) -> str:
            if v is None:
                return "NULL"
            if isinstance(v, str):
                return f"'{v}'"
            return str(v)

        value_lines.append(
            f"  ({q(r['symbol'])}, {q(r['timeframe'])}, {q(r['ts'])}, "
            f"{q(r['open'])}, {q(r['high'])}, {q(r['low'])}, {q(r['close'])}, "
            f"{q(r['volume'])}, {q(r['vwap'])}, {q(r['trade_count'])}, {q(r['inserted_at'])})"
        )
    lines.append(",\n".join(value_lines) + ";")
    return "\n".join(lines)


def rows_to_sql_news(rows: list[dict[str, Any]]) -> str:
    """Generate INSERT OR IGNORE SQL for news_sentiment."""
    if not rows:
        return "-- No rows to insert"

    lines = [
        "INSERT OR IGNORE INTO news_sentiment",
        "  (id, symbol, headline, summary, content, author, source, url, published_at, inserted_at)",
        "VALUES"
    ]
    value_lines = []
    for r in rows:
        def q(v: Any) -> str:
            if v is None:
                return "NULL"
            if isinstance(v, str):
                escaped = v.replace("'", "''")
                return f"'{escaped}'"
            return str(v)

        value_lines.append(
            f"  ({q(r['id'])}, {q(r['symbol'])}, {q(r['headline'])}, {q(r['summary'])}, "
            f"{q(r['content'])}, {q(r['author'])}, {q(r['source'])}, {q(r['url'])}, "
            f"{q(r['published_at'])}, {q(r['inserted_at'])})"
        )
    lines.append(",\n".join(value_lines) + ";")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize raw Alpaca MCP responses into DuckDB-ready rows.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- bars --
    bars_p = sub.add_parser("bars", help="Normalize get-stock-bars response")
    bars_p.add_argument("--input",     help="Path to JSON file (omit to read stdin)")
    bars_p.add_argument("--timeframe", required=True, help="Timeframe used in the request, e.g. 1Day")
    bars_p.add_argument("--format",    choices=("json", "sql"), default="json")
    bars_p.add_argument("--output",    help="Write output to this file instead of stdout")

    # -- news --
    news_p = sub.add_parser("news", help="Normalize get-news response")
    news_p.add_argument("--input",  help="Path to JSON file (omit to read stdin)")
    news_p.add_argument("--format", choices=("json", "sql"), default="json")
    news_p.add_argument("--output", help="Write output to this file instead of stdout")

    return parser.parse_args()


def load_input(path: str | None) -> Any:
    if path:
        with open(path) as f:
            return json.load(f)
    raw = sys.stdin.read().strip()
    if not raw:
        print("Error: no input provided (pipe JSON or use --input)", file=sys.stderr)
        sys.exit(1)
    return json.loads(raw)


def main() -> None:
    args = parse_args()
    data = load_input(args.input)

    if args.command == "bars":
        rows = normalize_bars(data, args.timeframe)
        out = rows_to_sql_bars(rows) if args.format == "sql" else rows_to_json(rows)
    else:  # news
        rows = normalize_news(data)
        out = rows_to_sql_news(rows) if args.format == "sql" else rows_to_json(rows)

    summary = {
        "command":   args.command,
        "rows":      len(rows),
        "format":    args.format,
    }
    print(f"-- normalized {len(rows)} rows", file=sys.stderr)

    if args.output:
        with open(args.output, "w") as f:
            f.write(out)
        print(f"-- written to {args.output}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
