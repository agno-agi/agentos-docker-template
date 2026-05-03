#!/usr/bin/env python3
"""
Bulk insert normalized JSON rows into the NanoQuant DuckDB trading database.

Used when MCP payload size limits would make one-by-one insertion slow or
impractical (e.g. months of 1-minute bars). Reads rows from a JSON file or
stdin and inserts directly via the DuckDB Python library.

Supported tables:
  ohlcv_bars       — OHLCV price/volume history from Alpaca
  news_sentiment   — News articles from Alpaca
  stockfit_signals — Screener/signal results from Stockfit
  trade_log        — Executed or simulated trades

Usage:
  # Insert bars from normalized JSON file
  python bulk_insert.py --table ohlcv_bars --input bars_rows.json

  # Pipe from normalize_alpaca.py
  python normalize_alpaca.py bars --input raw_alpaca.json --timeframe 1Day \\
    | python bulk_insert.py --table ohlcv_bars

  # Insert from file with a custom DB path
  python bulk_insert.py --table news_sentiment --input news_rows.json \\
    --db ~/custom/nanoquant.db

  # Dry run (validate rows without inserting)
  python bulk_insert.py --table ohlcv_bars --input bars.json --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_DB = Path.home() / ".openclaw" / "duckdb" / "trading.db"

# Required fields per table (used for validation)
REQUIRED_FIELDS: dict[str, list[str]] = {
    "ohlcv_bars":       ["symbol", "timeframe", "ts"],
    "news_sentiment":   ["id", "symbol"],
    "stockfit_signals": ["symbol", "signal_date", "signal_type"],
    "trade_log":        ["symbol", "side"],
}

# INSERT mode per table
INSERT_MODE: dict[str, str] = {
    "ohlcv_bars":       "INSERT OR IGNORE",
    "news_sentiment":   "INSERT OR IGNORE",
    "stockfit_signals": "INSERT OR REPLACE",
    "trade_log":        "INSERT OR IGNORE",
}


def get_db(db_path: Path) -> "duckdb.DuckDBPyConnection":  # noqa: F821
    try:
        import duckdb
    except ImportError:
        print("Error: duckdb not installed. Run: pip install duckdb --break-system-packages", file=sys.stderr)
        sys.exit(1)

    if not db_path.exists():
        print(f"Error: database not found at {db_path}", file=sys.stderr)
        print("Run init_db.py first to create the database and tables.", file=sys.stderr)
        sys.exit(1)

    return duckdb.connect(str(db_path))


def validate_rows(rows: list[dict[str, Any]], table: str) -> list[str]:
    """Return list of validation errors (empty = all good)."""
    errors: list[str] = []
    required = REQUIRED_FIELDS.get(table, [])

    if not isinstance(rows, list):
        return [f"Input must be a JSON array of objects, got {type(rows).__name__}"]

    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"Row {i}: expected object, got {type(row).__name__}")
            continue
        for field in required:
            if field not in row or row[field] is None:
                errors.append(f"Row {i}: missing required field '{field}'")

    return errors


def insert_rows(
    con: "duckdb.DuckDBPyConnection",  # noqa: F821
    table: str,
    rows: list[dict[str, Any]],
    batch_size: int = 500,
) -> dict[str, int]:
    """Insert rows using DuckDB's executemany for efficiency. Returns stats."""
    if not rows:
        return {"inserted": 0, "skipped": 0, "errors": 0}

    # Build column list from first row's keys (consistent with schema)
    columns = list(rows[0].keys())
    placeholders = ", ".join(["?"] * len(columns))
    col_list = ", ".join(columns)
    mode = INSERT_MODE.get(table, "INSERT OR IGNORE")
    sql = f"{mode} INTO {table} ({col_list}) VALUES ({placeholders})"

    inserted = 0
    errors = 0

    # Process in batches
    for batch_start in range(0, len(rows), batch_size):
        batch = rows[batch_start : batch_start + batch_size]
        values = [[row.get(col) for col in columns] for row in batch]

        try:
            con.executemany(sql, values)
            inserted += len(batch)
            print(
                f"  Inserted batch {batch_start // batch_size + 1} "
                f"({batch_start + 1}–{batch_start + len(batch)} of {len(rows)})",
                file=sys.stderr,
            )
        except Exception as exc:
            print(f"  Error in batch {batch_start // batch_size + 1}: {exc}", file=sys.stderr)
            errors += len(batch)

    return {"inserted": inserted, "skipped": 0, "errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bulk insert normalized JSON rows into NanoQuant DuckDB.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--table",
        required=True,
        choices=list(REQUIRED_FIELDS.keys()),
        help="Target table name",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to JSON file containing row array (omit to read stdin)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help=f"Path to DuckDB file (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Rows per insert batch (default: 500)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate rows without inserting",
    )
    args = parser.parse_args()

    # Load input
    if args.input:
        with open(args.input) as f:
            rows = json.load(f)
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            print("Error: no input (pipe JSON or use --input)", file=sys.stderr)
            sys.exit(1)
        rows = json.loads(raw)

    print(f"Table:    {args.table}", file=sys.stderr)
    print(f"Database: {args.db}", file=sys.stderr)
    print(f"Rows:     {len(rows):,}", file=sys.stderr)

    # Validate
    errors = validate_rows(rows, args.table)
    if errors:
        print(f"\nValidation failed ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors[:20]:
            print(f"  {e}", file=sys.stderr)
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more", file=sys.stderr)
        sys.exit(1)

    print("Validation passed.", file=sys.stderr)

    if args.dry_run:
        print("Dry run — no rows inserted.", file=sys.stderr)
        print(json.dumps({"dry_run": True, "rows_validated": len(rows), "table": args.table}))
        return

    # Insert
    con = get_db(args.db)
    stats = insert_rows(con, args.table, rows, batch_size=args.batch_size)
    con.close()

    print(json.dumps({
        "table":    args.table,
        "db":       str(args.db),
        "inserted": stats["inserted"],
        "errors":   stats["errors"],
    }, indent=2))

    if stats["errors"] > 0:
        print(f"\nCompleted with {stats['errors']} error(s).", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\nDone. {stats['inserted']:,} rows inserted into {args.table}.", file=sys.stderr)


if __name__ == "__main__":
    main()
