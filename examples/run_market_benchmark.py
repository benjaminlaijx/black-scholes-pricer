"""
Run the pricer against real market quotes and report pricing error.

Usage:
    1. Fill in examples/sample_quotes.csv with REAL quotes pulled from
       a live options chain (strike, expiry, market price, and either
       the quoted implied vol or your own vol estimate).
    2. python examples/run_market_benchmark.py
"""
import pandas as pd
from src.benchmark import price_quotes, summary_stats


def main():
    quotes = pd.read_csv("examples/sample_quotes.csv")

    if quotes["underlying"].str.startswith("PLACEHOLDER").any():
        print(
            "WARNING: sample_quotes.csv still contains placeholder rows.\n"
            "Replace S, market_price, and sigma with real numbers from a "
            "live options chain before treating these results as real "
            "validation.\n"
        )

    priced = price_quotes(quotes)
    stats = summary_stats(priced)

    print(priced[[
        "underlying", "K", "option_type", "market_price",
        "model_price", "abs_error", "pct_error",
    ]].to_string(index=False))

    print("\nSummary:")
    for k, v in stats.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")


if __name__ == "__main__":
    main()
