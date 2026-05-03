#!/usr/bin/env python3
"""
Initialize the NanoQuant DuckDB trading database.

Creates all four NanoQuant tables if they don't already exist.
Safe to run multiple times — uses CREATE TABLE IF NOT EXISTS.

Usage:
  python init_db.py
  python init_db.py --db ~/.openclaw/duckdb/trading.db
  python init_db.py --db ~/custom/path/nanoquant.db --verify
  python init_db.py --verify        # just check existing schema, don't create
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


DEFAULT_DB = Path.home() / ".openclaw" / "duckdb" / "trading.db"

TABLES: dict[str, str] = {
    "ohlcv_bars": """
        CREATE TABLE IF NOT EXISTS ohlcv_bars (
            symbol      VARCHAR     NOT NULL,
            timeframe   VARCHAR     NOT NULL,
            ts          TIMESTAMPTZ NOT NULL,
            open        DOUBLE,
            high        DOUBLE,
            low         DOUBLE,
            close       DOUBLE,
            volume      BIGINT,
            vwap        DOUBLE,
            trade_count INTEGER,
            inserted_at TIMESTAMPTZ DEFAULT now(),
            PRIMARY KEY (symbol, timeframe, ts)
        )
    """,
    "news_sentiment": """
        CREATE TABLE IF NOT EXISTS news_sentiment (
            id           BIGINT      PRIMARY KEY,
            symbol       VARCHAR     NOT NULL,
            headline     VARCHAR,
            summary      TEXT,
            content      TEXT,
            author       VARCHAR,
            source       VARCHAR,
            url          VARCHAR,
            published_at TIMESTAMPTZ,
            inserted_at  TIMESTAMPTZ DEFAULT now()
        )
    """,
    "stockfit_signals": """
        CREATE TABLE IF NOT EXISTS stockfit_signals (
            id          VARCHAR     DEFAULT gen_random_uuid()::VARCHAR,
            symbol      VARCHAR     NOT NULL,
            signal_date DATE        NOT NULL,
            signal_type VARCHAR,
            direction   VARCHAR,
            strength    DOUBLE,
            timeframe   VARCHAR,
            raw_data    JSON,
            inserted_at TIMESTAMPTZ DEFAULT now(),
            PRIMARY KEY (symbol, signal_date, signal_type)
        )
    """,
    "trade_log": """
        CREATE TABLE IF NOT EXISTS trade_log (
            id          VARCHAR     DEFAULT gen_random_uuid()::VARCHAR PRIMARY KEY,
            symbol      VARCHAR     NOT NULL,
            side        VARCHAR     NOT NULL,
            entry_price DOUBLE,
            exit_price  DOUBLE,
            qty         DOUBLE,
            entry_at    TIMESTAMPTZ,
            exit_at     TIMESTAMPTZ,
            pnl         DOUBLE,
            pnl_pct     DOUBLE,
            strategy    VARCHAR,
            notes       TEXT,
            inserted_at TIMESTAMPTZ DEFAULT now()
        )
    """,
}


def get_db(db_path: Path) -> "duckdb.DuckDBPyConnection":  # noqa: F821
    try:
        import duckdb
    except ImportError:
        print("Error: duckdb not installed. Run: pip install duckdb --break-system-packages", file=sys.stderr)
        sys.exit(1)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path))


def create_tables(con: "duckdb.DuckDBPyConnection") -> dict[str, str]:  # noqa: F821
    results: dict[str, str] = {}
    for name, ddl in TABLES.items():
        try:
            con.execute(ddl)
            results[name] = "created/verified"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"
    return results


def verify_schema(con: "duckdb.DuckDBPyConnection") -> dict[str, Any]:  # noqa: F821
    from typing import Any
    report: dict[str, Any] = {}
    existing = {row[0] for row in con.execute("SHOW TABLES").fetchall()}

    for name in TABLES:
        if name not in existing:
            report[name] = {"exists": False, "columns": []}
            continue
        cols = con.execute(f"DESCRIBE {name}").fetchall()
        report[name] = {
            "exists": True,
            "row_count": con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0],
            "columns": [{"name": c[0], "type": c[1]} for c in cols],
        }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize NanoQuant DuckDB trading database.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help=f"Path to DuckDB file (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Show current schema and row counts without creating tables",
    )
    args = parser.parse_args()

    con = get_db(args.db)
    print(f"Database: {args.db}", file=sys.stderr)

    if args.verify:
        report = verify_schema(con)
        print(json.dumps(report, indent=2))
        missing = [t for t, v in report.items() if not v["exists"]]
        if missing:
            print(f"\nMissing tables: {missing}", file=sys.stderr)
            print("Run without --verify to create them.", file=sys.stderr)
            sys.exit(1)
        else:
            total_rows = sum(v["row_count"] for v in report.values())
            print(f"\nAll 4 tables present. Total rows: {total_rows:,}", file=sys.stderr)
    else:
        results = create_tables(con)
        for name, status in results.items():
            icon = "✓" if "ERROR" not in status else "✗"
            print(f"  {icon} {name}: {status}", file=sys.stderr)

        errors = {k: v for k, v in results.items() if "ERROR" in v}
        if errors:
            print(f"\n{len(errors)} table(s) failed to initialize.", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"\nAll {len(TABLES)} tables initialized successfully.", file=sys.stderr)

        # Print verify report after creation
        report = verify_schema(con)
        print(json.dumps(report, indent=2))

    con.close()


if __name__ == "__main__":
    main()
