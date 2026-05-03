#!/usr/bin/env python3
"""
Launch the official DuckDB browser UI against the NanoQuant trading database.

Checks DuckDB version compatibility (requires v1.2+), reports the URL,
and opens the browser automatically.

Usage:
  python launch_ui.py
  python launch_ui.py --db ~/.openclaw/duckdb/trading.db
  python launch_ui.py --db ~/custom/nanoquant.db --port 4214
  python launch_ui.py --no-browser   # start server without opening browser
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path


DEFAULT_DB   = Path.home() / ".openclaw" / "duckdb" / "trading.db"
DEFAULT_PORT = 4213
MIN_VERSION  = (1, 2, 0)


def find_duckdb() -> str | None:
    return shutil.which("duckdb")


def get_duckdb_version(binary: str) -> tuple[int, ...] | None:
    try:
        result = subprocess.run(
            [binary, "--version"],
            capture_output=True, text=True, timeout=5
        )
        # Output: "v1.2.1 ..."
        line = (result.stdout or result.stderr).strip()
        for part in line.split():
            cleaned = part.lstrip("v")
            if cleaned[0].isdigit():
                try:
                    return tuple(int(x) for x in cleaned.split(".")[:3])
                except ValueError:
                    continue
    except Exception:
        pass
    return None


def version_str(v: tuple[int, ...]) -> str:
    return ".".join(str(x) for x in v)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Launch DuckDB official browser UI for NanoQuant trading database.",
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
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port for the UI server (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start the server without auto-opening the browser",
    )
    args = parser.parse_args()

    # Find DuckDB binary
    binary = find_duckdb()
    if not binary:
        print("Error: duckdb not found in PATH.", file=sys.stderr)
        print("Install it: brew install duckdb", file=sys.stderr)
        sys.exit(1)

    # Check version
    version = get_duckdb_version(binary)
    if version:
        print(f"DuckDB version: v{version_str(version)}", file=sys.stderr)
        if version < MIN_VERSION:
            print(
                f"Warning: DuckDB v{version_str(MIN_VERSION)}+ required for -ui flag. "
                f"You have v{version_str(version)}.",
                file=sys.stderr,
            )
            print("Upgrade: brew upgrade duckdb", file=sys.stderr)
            sys.exit(1)
    else:
        print("Warning: Could not determine DuckDB version.", file=sys.stderr)

    # Check DB file
    if not args.db.exists():
        print(f"Warning: Database file not found at {args.db}", file=sys.stderr)
        print("The UI will create a new empty database at that path.", file=sys.stderr)
        print("Run init_db.py first to create the NanoQuant tables.", file=sys.stderr)
    else:
        size_mb = args.db.stat().st_size / 1_048_576
        print(f"Database: {args.db} ({size_mb:.1f} MB)", file=sys.stderr)

    url = f"http://localhost:{args.port}"
    print(f"\nStarting DuckDB UI at {url}", file=sys.stderr)
    print("Press Ctrl+C to stop.\n", file=sys.stderr)

    if not args.no_browser:
        # Open browser after a short delay (server needs a moment to start)
        import threading
        import time
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(url)
        threading.Thread(target=open_browser, daemon=True).start()

    # Launch DuckDB UI — this blocks until Ctrl+C
    cmd = [binary, str(args.db), "-ui"]
    if args.port != DEFAULT_PORT:
        # DuckDB UI port flag (available in newer versions)
        cmd += [f"--ui-port={args.port}"]

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nDuckDB UI stopped.", file=sys.stderr)
    except subprocess.CalledProcessError as exc:
        print(f"\nDuckDB exited with error code {exc.returncode}.", file=sys.stderr)
        if exc.returncode == 1:
            print(
                "If you see 'unknown option: -ui', your DuckDB version is too old. "
                "Run: brew upgrade duckdb",
                file=sys.stderr,
            )
        sys.exit(exc.returncode)


if __name__ == "__main__":
    main()
