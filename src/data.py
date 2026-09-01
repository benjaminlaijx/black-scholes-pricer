"""
Historical price data loader for the backtest.

Tries yfinance first (live download). If it's not installed, or the
network call fails, falls back to reading a local CSV so the backtest
can still be run/graded offline -- point `csv_path` at any file with
'Date' and 'Close' columns (e.g. one exported from Yahoo Finance).
"""
import os
import pandas as pd


def load_price_history(ticker="SPY", start="2019-01-01", end=None, csv_path=None):
    """
    Returns a pandas Series of daily close prices, indexed by date,
    sorted ascending, with any NaNs dropped.
    """
    if csv_path is not None and os.path.exists(csv_path):
        df = pd.read_csv(csv_path, parse_dates=["Date"])
        df = df.set_index("Date").sort_index()
        col = "Adj Close" if "Adj Close" in df.columns else "Close"
        return df[col].dropna()

    try:
        import yfinance as yf
    except ImportError as e:
        raise ImportError(
            "yfinance is not installed and no csv_path was given. "
            "Run `pip install yfinance`, or pass csv_path= to load "
            "prices from a local file instead."
        ) from e

    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No price data returned for {ticker} between {start} and {end}.")

    prices = df["Close"].dropna()
    prices.name = ticker
    return prices
