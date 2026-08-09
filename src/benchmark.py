"""
Benchmark the closed-form pricer against real market option quotes.

This is NOT a live data fetch -- it takes a small table of real quotes
(strike, expiry, market price, implied vol if known, and the inputs
needed to reprice: S, r, sigma) and compares the model's price against
what the market actually printed. Populate `sample_quotes.csv` with
real numbers pulled from a live options chain (e.g. an exchange site
or broker) before running this for real.
"""
import numpy as np
import pandas as pd

from .black_scholes import call_price, put_price


def price_quotes(df):
    """
    df must have columns: S, K, r, sigma, T, market_price, option_type.
    Returns df with model_price, abs_error, pct_error added.
    """
    df = df.copy()
    model_prices = []
    for _, row in df.iterrows():
        fn = call_price if row["option_type"] == "call" else put_price
        model_prices.append(fn(row["S"], row["K"], row["r"], row["sigma"], row["T"]))
    df["model_price"] = model_prices
    df["abs_error"] = df["model_price"] - df["market_price"]
    df["pct_error"] = df["abs_error"] / df["market_price"] * 100
    return df


def summary_stats(df):
    """Mean absolute error, mean pct error, max abs error -- the numbers
    you'd actually want to quote in an interview rather than eyeballing
    a table."""
    return {
        "n_quotes": len(df),
        "mean_abs_error": df["abs_error"].abs().mean(),
        "mean_pct_error": df["pct_error"].abs().mean(),
        "max_abs_error": df["abs_error"].abs().max(),
    }
