"""
Backtests a systematic covered-call overlay on SPY, priced with this
repo's own Black-Scholes engine, against a buy-and-hold benchmark.

Usage:
    python examples/run_backtest.py

Requires `pip install yfinance` for live data. If you don't have
network access, pass --csv path/to/spy_prices.csv (columns: Date, Close
or Adj Close -- e.g. exported from Yahoo Finance / stooq.com).
"""
import argparse
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data import load_price_history
from src.backtest import run_covered_call_backtest, performance_metrics

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", default="SPY")
    parser.add_argument("--start", default="2019-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--otm-pct", type=float, default=0.03)
    parser.add_argument("--hold-days", type=int, default=21)
    parser.add_argument("--r", type=float, default=0.02)
    parser.add_argument("--csv", default=None, help="local CSV fallback if offline")
    args = parser.parse_args()

    prices = load_price_history(
        ticker=args.ticker, start=args.start, end=args.end, csv_path=args.csv
    )
    print(f"Loaded {len(prices):,} daily prices for {args.ticker} "
          f"({prices.index[0].date()} to {prices.index[-1].date()})\n")

    results = run_covered_call_backtest(
        prices, otm_pct=args.otm_pct, hold_days=args.hold_days, r=args.r
    )

    periods_per_year = 252 / args.hold_days
    strat_metrics = performance_metrics(results["strategy_nav"], periods_per_year, r=args.r)
    bench_metrics = performance_metrics(results["benchmark_nav"], periods_per_year, r=args.r)

    summary = {
        "Covered call (this strategy)": strat_metrics,
        "Buy-and-hold (benchmark)": bench_metrics,
    }

    print(f"Covered-call backtest: {args.otm_pct:.0%} OTM, "
          f"{args.hold_days}-trading-day tenor, r={args.r:.1%}\n")
    print(f"{'Metric':<20}{'Covered Call':>16}{'Buy-and-Hold':>16}")
    for key in ["CAGR", "annualized_vol", "sharpe_ratio", "max_drawdown", "win_rate"]:
        s, b = strat_metrics[key], bench_metrics[key]
        if key == "sharpe_ratio":
            print(f"{key:<20}{s:>16.2f}{b:>16.2f}")
        else:
            print(f"{key:<20}{s:>15.1%} {b:>15.1%}")
    print(f"{'n_periods':<20}{strat_metrics['n_periods']:>16d}{bench_metrics['n_periods']:>16d}")
    print()

    # Plot: equity curves.
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(results.index, results["strategy_nav"], label="Covered call overlay")
    ax.plot(results.index, results["benchmark_nav"], label="Buy-and-hold", linestyle="--")
    ax.set_title(f"{args.ticker}: Covered Call Overlay vs. Buy-and-Hold")
    ax.set_ylabel("Growth of $1")
    ax.legend()
    plt.tight_layout()
    plot_path = os.path.join(OUT_DIR, "backtest_equity_curve.png")
    plt.savefig(plot_path, dpi=150)
    print(f"Saved equity curve plot to {plot_path}")

    csv_path = os.path.join(OUT_DIR, "backtest_results.csv")
    results.to_csv(csv_path)
    print(f"Saved period-by-period results to {csv_path}")


if __name__ == "__main__":
    main()
