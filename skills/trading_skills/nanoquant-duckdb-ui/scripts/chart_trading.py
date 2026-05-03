#!/usr/bin/env python3
"""
Generate interactive trading charts from the NanoQuant DuckDB database.

All charts are rendered as self-contained HTML files using Plotly.js —
no static images, fully interactive (zoom, pan, hover, crosshair).

Requires: pip install plotly duckdb --break-system-packages

Usage:
  # Candlestick + volume for SPY last 30 days
  python chart_trading.py ohlcv --symbol SPY --timeframe 1Day --days 30

  # Candlestick for ES last 5 days at 1-hour bars
  python chart_trading.py ohlcv --symbol ES --timeframe 1Hour --days 5

  # Cumulative P&L equity curve (all strategies)
  python chart_trading.py equity

  # Equity curve for a specific strategy
  python chart_trading.py equity --strategy ORB

  # Signal strength + count over time
  python chart_trading.py signals --symbol MES --days 60

  # Trade returns distribution histogram
  python chart_trading.py returns

  # Custom output path
  python chart_trading.py ohlcv --symbol SPY --timeframe 1Day --days 30 --output ~/Desktop/spy.html

All charts auto-open in your default browser after generation.
Charts are saved to ~/.openclaw/charts/ by default.
"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


DEFAULT_DB  = Path.home() / ".openclaw" / "duckdb" / "trading.db"
OUTPUT_DIR  = Path.home() / ".openclaw" / "charts"

DARK_BG     = "#0d1117"
DARK_PANEL  = "#161b22"
DARK_GRID   = "#21262d"
TEXT_COLOR  = "#e6edf3"
GREEN       = "#3fb950"
RED         = "#f85149"
BLUE        = "#58a6ff"
YELLOW      = "#d29922"
PURPLE      = "#bc8cff"
ORANGE      = "#ffa657"


def get_db(db_path: Path) -> "duckdb.DuckDBPyConnection":  # noqa: F821
    try:
        import duckdb
    except ImportError:
        print("Error: pip install duckdb --break-system-packages", file=sys.stderr)
        sys.exit(1)
    if not db_path.exists():
        print(f"Error: database not found at {db_path}", file=sys.stderr)
        print("Run init_db.py first.", file=sys.stderr)
        sys.exit(1)
    return duckdb.connect(str(db_path), read_only=True)


def get_plotly() -> Any:
    try:
        import plotly.graph_objects as go
        return go
    except ImportError:
        print("Error: pip install plotly --break-system-packages", file=sys.stderr)
        sys.exit(1)


def ensure_output(path: Path | None, default_name: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return path or OUTPUT_DIR / f"{default_name}.html"


def base_layout(title: str, **extra) -> dict:
    """Shared dark-theme Plotly layout."""
    return dict(
        title=dict(text=title, font=dict(color=TEXT_COLOR, size=15)),
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_PANEL,
        font=dict(color=TEXT_COLOR, family="monospace"),
        xaxis=dict(gridcolor=DARK_GRID, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=DARK_GRID, showgrid=True, zeroline=False),
        legend=dict(bgcolor=DARK_PANEL, bordercolor=DARK_GRID, borderwidth=1),
        margin=dict(l=60, r=30, t=60, b=50),
        hovermode="x unified",
        **extra,
    )


def save_and_open(fig: Any, output: Path) -> None:
    fig.write_html(
        str(output),
        include_plotlyjs="cdn",      # loads plotly.js from CDN — no local install needed
        full_html=True,
        config={
            "displayModeBar": True,
            "scrollZoom": True,
            "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
        },
    )
    print(f"Chart saved: {output}", file=sys.stderr)
    webbrowser.open(str(output))


# ---------------------------------------------------------------------------
# OHLCV Candlestick + Volume
# ---------------------------------------------------------------------------

def chart_ohlcv(con: Any, symbol: str, timeframe: str, days: int, output: Path) -> None:
    go = get_plotly()
    from plotly.subplots import make_subplots

    since = (datetime.now(UTC) - timedelta(days=days)).isoformat()
    rows = con.execute("""
        SELECT ts, open, high, low, close, volume, vwap
        FROM ohlcv_bars
        WHERE symbol = ? AND timeframe = ? AND ts >= ?
        ORDER BY ts
    """, [symbol, timeframe, since]).fetchall()

    if not rows:
        print(f"No data for {symbol} ({timeframe}) in the last {days} days.", file=sys.stderr)
        print("Run the Alpaca pipeline first to populate ohlcv_bars.", file=sys.stderr)
        sys.exit(1)

    print(f"Charting {len(rows)} bars — {symbol} {timeframe}", file=sys.stderr)

    dates  = [r[0] for r in rows]
    opens  = [r[1] for r in rows]
    highs  = [r[2] for r in rows]
    lows   = [r[3] for r in rows]
    closes = [r[4] for r in rows]
    vols   = [r[5] or 0 for r in rows]
    vwaps  = [r[6] for r in rows]

    bar_colors = [GREEN if c >= o else RED for o, c in zip(opens, closes)]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.75, 0.25],
        subplot_titles=["", "Volume"],
    )

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=dates, open=opens, high=highs, low=lows, close=closes,
        name=symbol,
        increasing=dict(line=dict(color=GREEN), fillcolor=GREEN),
        decreasing=dict(line=dict(color=RED),   fillcolor=RED),
        whiskerwidth=0.5,
    ), row=1, col=1)

    # VWAP overlay
    if any(v is not None for v in vwaps):
        fig.add_trace(go.Scatter(
            x=dates, y=vwaps, name="VWAP",
            line=dict(color=ORANGE, width=1.5, dash="dot"),
            opacity=0.85,
        ), row=1, col=1)

    # Volume bars
    fig.add_trace(go.Bar(
        x=dates, y=vols, name="Volume",
        marker_color=bar_colors,
        marker_opacity=0.6,
        showlegend=False,
    ), row=2, col=1)

    layout = base_layout(f"{symbol} — {timeframe} · last {days}d")
    layout.update(
        xaxis=dict(rangeslider=dict(visible=False), gridcolor=DARK_GRID, zeroline=False),
        xaxis2=dict(gridcolor=DARK_GRID, zeroline=False),
        yaxis=dict(gridcolor=DARK_GRID, zeroline=False, title="Price"),
        yaxis2=dict(gridcolor=DARK_GRID, zeroline=False, title="Volume"),
        height=650,
    )
    fig.update_layout(**layout)
    save_and_open(fig, output)


# ---------------------------------------------------------------------------
# Equity Curve
# ---------------------------------------------------------------------------

def chart_equity(con: Any, strategy: str | None, output: Path) -> None:
    go = get_plotly()

    where  = "WHERE pnl IS NOT NULL" + (" AND strategy = ?" if strategy else "")
    params = [strategy] if strategy else []
    rows   = con.execute(
        f"SELECT exit_at, pnl, strategy FROM trade_log {where} ORDER BY exit_at",
        params
    ).fetchall()

    if not rows:
        print("No trades found in trade_log.", file=sys.stderr)
        sys.exit(1)

    print(f"Charting equity curve — {len(rows)} trades", file=sys.stderr)

    dates      = [r[0] for r in rows]
    pnls       = [r[1] or 0 for r in rows]
    strategies = [r[2] for r in rows]

    cumulative = []
    running = 0.0
    for p in pnls:
        running += p
        cumulative.append(running)

    # Color fill: split into positive and negative segments
    pos_y = [v if v >= 0 else 0 for v in cumulative]
    neg_y = [v if v < 0 else 0 for v in cumulative]

    fig = go.Figure()

    # Positive fill
    fig.add_trace(go.Scatter(
        x=dates, y=pos_y, name="Profit",
        fill="tozeroy",
        line=dict(color=GREEN, width=0),
        fillcolor=f"rgba(63,185,80,0.15)",
        hoverinfo="skip",
        showlegend=False,
    ))
    # Negative fill
    fig.add_trace(go.Scatter(
        x=dates, y=neg_y, name="Loss",
        fill="tozeroy",
        line=dict(color=RED, width=0),
        fillcolor=f"rgba(248,81,73,0.15)",
        hoverinfo="skip",
        showlegend=False,
    ))
    # Main equity line
    fig.add_trace(go.Scatter(
        x=dates, y=cumulative,
        name="Cumulative P&L",
        mode="lines",
        line=dict(color=GREEN if cumulative[-1] >= 0 else RED, width=2),
        hovertemplate="%{x}<br>P&L: $%{y:,.2f}<extra></extra>",
    ))
    # Individual trade markers
    fig.add_trace(go.Scatter(
        x=dates, y=cumulative,
        name="Trades",
        mode="markers",
        marker=dict(
            color=[GREEN if p >= 0 else RED for p in pnls],
            size=5, opacity=0.7,
        ),
        hovertemplate="%{x}<br>Trade: $%{customdata:,.2f}<br>Cumulative: $%{y:,.2f}<extra></extra>",
        customdata=pnls,
    ))

    fig.add_hline(y=0, line_dash="dot", line_color=DARK_GRID, line_width=1.5)

    title = f"Equity Curve — {strategy or 'All Strategies'} ({len(rows)} trades)"
    fig.update_layout(**base_layout(title, yaxis_title="Cumulative P&L ($)", height=520))
    save_and_open(fig, output)


# ---------------------------------------------------------------------------
# Signals Chart
# ---------------------------------------------------------------------------

def chart_signals(con: Any, symbol: str | None, days: int, output: Path) -> None:
    go = get_plotly()
    from plotly.subplots import make_subplots

    since  = (datetime.now(UTC) - timedelta(days=days)).date().isoformat()
    where  = "WHERE signal_date >= ?" + (" AND symbol = ?" if symbol else "")
    params = [since] + ([symbol] if symbol else [])

    rows = con.execute(f"""
        SELECT signal_date,
               AVG(strength)                                         AS avg_strength,
               COUNT(*)                                              AS total,
               SUM(CASE WHEN direction = 'long'  THEN 1 ELSE 0 END) AS longs,
               SUM(CASE WHEN direction = 'short' THEN 1 ELSE 0 END) AS shorts
        FROM stockfit_signals
        {where}
        GROUP BY signal_date ORDER BY signal_date
    """, params).fetchall()

    if not rows:
        print("No signals found in stockfit_signals.", file=sys.stderr)
        sys.exit(1)

    print(f"Charting {sum(r[2] for r in rows)} signals across {len(rows)} days", file=sys.stderr)

    dates    = [r[0] for r in rows]
    strength = [r[1] or 0 for r in rows]
    totals   = [r[2] for r in rows]
    longs    = [r[3] for r in rows]
    shorts   = [r[4] for r in rows]

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.4],
    )

    # Signal strength line
    fig.add_trace(go.Scatter(
        x=dates, y=strength, name="Avg Strength",
        mode="lines+markers",
        line=dict(color=YELLOW, width=2),
        marker=dict(size=6, color=YELLOW),
        hovertemplate="%{x}<br>Strength: %{y:.3f}<extra></extra>",
    ), row=1, col=1)

    # Long/short stacked bars
    fig.add_trace(go.Bar(
        x=dates, y=longs, name="Long",
        marker_color=GREEN, opacity=0.75,
        hovertemplate="%{x}<br>Longs: %{y}<extra></extra>",
    ), row=2, col=1)
    fig.add_trace(go.Bar(
        x=dates, y=shorts, name="Short",
        marker_color=RED, opacity=0.75,
        hovertemplate="%{x}<br>Shorts: %{y}<extra></extra>",
    ), row=2, col=1)

    title = f"Stockfit Signals — {symbol or 'All Symbols'} · last {days}d"
    layout = base_layout(title)
    layout.update(
        barmode="stack",
        yaxis=dict(gridcolor=DARK_GRID, zeroline=False, title="Avg Strength"),
        yaxis2=dict(gridcolor=DARK_GRID, zeroline=False, title="Count"),
        height=560,
    )
    fig.update_layout(**layout)
    save_and_open(fig, output)


# ---------------------------------------------------------------------------
# Returns Distribution
# ---------------------------------------------------------------------------

def chart_returns(con: Any, strategy: str | None, output: Path) -> None:
    go = get_plotly()

    where  = "WHERE pnl_pct IS NOT NULL" + (" AND strategy = ?" if strategy else "")
    params = [strategy] if strategy else []
    rows   = con.execute(
        f"SELECT pnl_pct, pnl, symbol, strategy FROM trade_log {where}",
        params
    ).fetchall()

    if not rows:
        print("No trade returns in trade_log.", file=sys.stderr)
        sys.exit(1)

    print(f"Charting returns distribution — {len(rows)} trades", file=sys.stderr)

    returns   = [r[0] for r in rows]
    pnls      = [r[1] or 0 for r in rows]
    symbols   = [r[2] for r in rows]
    strats    = [r[3] for r in rows]

    wins  = sum(1 for r in returns if r >= 0)
    losses = len(returns) - wins
    avg_r  = sum(returns) / len(returns)
    total_pnl = sum(pnls)

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=returns,
        nbinsx=50,
        name="Returns",
        marker=dict(
            color=[GREEN if r >= 0 else RED for r in returns],
            line=dict(color=DARK_BG, width=0.5),
        ),
        opacity=0.85,
        hovertemplate="Return: %{x:.2f}%<br>Count: %{y}<extra></extra>",
    ))

    # Zero line
    fig.add_vline(x=0,       line_dash="solid", line_color=TEXT_COLOR, line_width=1, opacity=0.4)
    # Mean line
    fig.add_vline(x=avg_r,   line_dash="dash",  line_color=YELLOW,     line_width=1.5,
                  annotation_text=f"Mean {avg_r:.2f}%", annotation_font_color=YELLOW)

    win_rate = wins / len(returns) * 100
    title = (
        f"Returns Distribution — {strategy or 'All Strategies'} · "
        f"n={len(returns)} · Win rate {win_rate:.1f}% · "
        f"Total P&L ${total_pnl:,.0f}"
    )
    layout = base_layout(title, xaxis_title="Return (%)", yaxis_title="Trade Count")
    layout.update(showlegend=False, height=480)
    fig.update_layout(**layout)
    save_and_open(fig, output)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate interactive Plotly.js trading charts from NanoQuant DuckDB.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--db",     type=Path, default=DEFAULT_DB, help="DuckDB file path")
    parser.add_argument("--output", type=Path, help="Output HTML file path")
    sub = parser.add_subparsers(dest="chart", required=True)

    ohlcv_p = sub.add_parser("ohlcv", help="Candlestick + volume + VWAP")
    ohlcv_p.add_argument("--symbol",    required=True, help="Ticker symbol e.g. SPY")
    ohlcv_p.add_argument("--timeframe", default="1Day", help="Bar timeframe e.g. 1Day, 1Hour")
    ohlcv_p.add_argument("--days",      type=int, default=30, help="Number of days back")

    eq_p = sub.add_parser("equity", help="Cumulative P&L equity curve")
    eq_p.add_argument("--strategy", help="Filter by strategy name e.g. ORB")

    sig_p = sub.add_parser("signals", help="Signal strength over time")
    sig_p.add_argument("--symbol", help="Filter by symbol")
    sig_p.add_argument("--days",   type=int, default=30)

    ret_p = sub.add_parser("returns", help="Returns distribution histogram")
    ret_p.add_argument("--strategy", help="Filter by strategy name")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    con  = get_db(args.db)

    if args.chart == "ohlcv":
        out = ensure_output(args.output, f"ohlcv_{args.symbol}_{args.timeframe}_{args.days}d")
        chart_ohlcv(con, args.symbol, args.timeframe, args.days, out)

    elif args.chart == "equity":
        out = ensure_output(args.output, f"equity_{args.strategy or 'all'}")
        chart_equity(con, args.strategy, out)

    elif args.chart == "signals":
        out = ensure_output(args.output, f"signals_{args.symbol or 'all'}_{args.days}d")
        chart_signals(con, args.symbol, args.days, out)

    elif args.chart == "returns":
        out = ensure_output(args.output, f"returns_{args.strategy or 'all'}")
        chart_returns(con, args.strategy, out)

    con.close()


if __name__ == "__main__":
    main()
