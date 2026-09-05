"""
Benchmarks the closed-form pricer against real, live SPY option quotes.

Usage:
    python examples/run_market_validation.py
    python examples/run_market_validation.py --expiry 2026-01-16 --r 0.02

Requires `pip install yfinance` and a live internet connection -- this
pulls the current option chain, so results will differ depending on
when you run it.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.market_validation import (
    fetch_spy_call_chain,
    compare_to_market,
    save_chain_snapshot,
    load_chain_snapshot,
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expiry", default=None, help="YYYY-MM-DD, defaults to nearest expiry")
    parser.add_argument("--r", type=float, default=0.02)
    parser.add_argument("--min-days-out", type=int, default=25,
                         help="skip expiries closer than this when auto-selecting (default 25)")
    parser.add_argument("--min-price", type=float, default=0.10,
                         help="drop quotes cheaper than this -- avoids tick-size noise (default 0.10)")
    parser.add_argument("--include-itm", action="store_true",
                         help="include in-the-money calls (off by default -- they're priced by intrinsic "
                              "value regardless of sigma, which isn't a real test of the model)")
    parser.add_argument("--csv", default=None, help="load a saved chain snapshot instead of a live fetch")
    parser.add_argument("--save-snapshot", action="store_true",
                         help="save the fetched chain to output/ so this run can be reproduced later")
    args = parser.parse_args()

    if args.csv:
        S, T, expiry, chain = load_chain_snapshot(args.csv)
        print(f"Loaded snapshot: SPY spot {S:.2f}, expiry {expiry} (T={T:.4f}y), {len(chain)} strikes\n")
    else:
        S, T, expiry, chain = fetch_spy_call_chain(expiry=args.expiry, min_days_out=args.min_days_out)
        print(f"SPY spot: {S:.2f}  |  Expiry: {expiry}  (T={T:.4f}y)  |  {len(chain)} strikes\n")
        if args.save_snapshot:
            snap_path = os.path.join(OUT_DIR, f"chain_snapshot_{expiry}.csv")
            save_chain_snapshot(S, T, expiry, chain, snap_path)
            print(f"Saved chain snapshot to {snap_path}\n")

    results, sigma_ref = compare_to_market(
        S, T, chain, r=args.r, otm_only=not args.include_itm, min_price=args.min_price
    )

    print(f"Reference sigma (implied vol at closest-to-ATM strike): {sigma_ref:.4f}\n")

    buckets = pd.cut(results["moneyness"], bins=[0, 0.02, 0.05, 0.10, 0.20, np.inf])
    summary = results.groupby(buckets, observed=True)["pct_error"].agg(["mean", "max", "count"])
    print("Pricing error by distance from spot (moneyness):")
    print(summary.to_string())
    print()

    csv_path = os.path.join(OUT_DIR, "market_validation.csv")
    results.to_csv(csv_path, index=False)
    print(f"Saved full comparison ({len(results)} strikes) to {csv_path}")


if __name__ == "__main__":
    main()
