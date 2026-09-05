"""
Validates the closed-form pricer against real SPY option quotes.

Methodology: pull the live SPY option chain for a given expiry, take the
implied volatility quoted at the strike closest to the money as a single
"reference" sigma, then price every strike in the chain with this repo's
own call_price() using that one constant sigma. Comparing the resulting
model prices to the market's actual quotes isolates exactly what a
constant-volatility model gets wrong: real option markets price a
volatility skew (different implied vol per strike), so a model that
assumes one flat sigma should track the market well near the reference
strike and increasingly diverge as strikes move away from it.
"""
import numpy as np
import pandas as pd

from .black_scholes import call_price


def fetch_spy_call_chain(expiry=None, min_days_out=25):
    """
    Pulls the live SPY spot price and call option chain via yfinance.

    Parameters
    ----------
    expiry : str, optional
        Expiration date as 'YYYY-MM-DD'. Defaults to the nearest expiry
        at least `min_days_out` days away.
    min_days_out : int
        Skips expiries closer than this when choosing a default. Very
        short-dated (0-5 day) contracts have almost no time value near
        the money, so their prices are dominated by bid-ask noise rather
        than the model -- a poor test of pricing accuracy.

    Returns
    -------
    (S, T, expiry, chain) where chain is a DataFrame with columns
    strike, bid, ask, lastPrice, impliedVolatility.
    """
    try:
        import yfinance as yf
    except ImportError as e:
        raise ImportError("yfinance is required: pip install yfinance") from e

    ticker = yf.Ticker("SPY")
    S = ticker.history(period="1d")["Close"].iloc[-1]

    expiries = ticker.options
    if not expiries:
        raise ValueError("No option expiries returned for SPY.")

    if expiry is None:
        today = pd.Timestamp.today()
        for candidate in expiries:
            if (pd.Timestamp(candidate) - today).days >= min_days_out:
                expiry = candidate
                break
        expiry = expiry or expiries[-1]  # fall back to the furthest available

    chain = ticker.option_chain(expiry).calls
    chain = chain[["strike", "bid", "ask", "lastPrice", "impliedVolatility"]].dropna()

    T = (pd.Timestamp(expiry) - pd.Timestamp.today()).days / 365.0
    return S, T, expiry, chain


def compare_to_market(S, T, chain, r=0.02, otm_only=True, min_price=0.10):
    """
    Prices every strike with a single constant sigma (the implied vol
    at the strike closest to S) and compares to the market's mid price.

    Parameters
    ----------
    otm_only : bool
        If True (default), keep only strikes at or above spot. In-the-
        money calls are priced mostly by intrinsic value, which any
        reasonable sigma gets right -- including them makes the "does a
        flat sigma mismatch the market away from ATM" test meaningless,
        since ITM strikes trivially show near-zero error regardless.
    min_price : float
        Drops quotes with mid price below this. Very cheap options have
        pricing dominated by bid-ask/tick-size noise rather than the
        model, which otherwise shows up as spurious large %% errors.

    Returns
    -------
    (results, sigma_ref) where results is a DataFrame with strike,
    market_mid, model_price, pct_error, and moneyness (|K - S| / S),
    sorted by moneyness.
    """
    atm_row = chain.iloc[(chain["strike"] - S).abs().argsort().iloc[0]]
    sigma_ref = atm_row["impliedVolatility"]

    chain = chain.copy()
    chain["market_mid"] = (chain["bid"] + chain["ask"]) / 2
    # A zero bid (common far from the money) collapses the mid price toward
    # zero and manufactures a fake ~100% pricing error that has nothing to
    # do with the model -- exclude quotes without a real two-sided market.
    chain = chain[(chain["bid"] > 0) & (chain["ask"] > 0)]
    chain = chain[chain["market_mid"] >= min_price]
    if otm_only:
        chain = chain[chain["strike"] >= S]

    chain["model_price"] = call_price(S, chain["strike"], r, sigma_ref, T)
    chain["pct_error"] = (chain["model_price"] - chain["market_mid"]).abs() / chain["market_mid"]
    chain["moneyness"] = (chain["strike"] - S).abs() / S

    results = chain[["strike", "moneyness", "market_mid", "model_price", "pct_error"]].sort_values("moneyness")
    return results, sigma_ref


def save_chain_snapshot(S, T, expiry, chain, path):
    """
    Saves the raw option chain plus spot/expiry metadata to a CSV, so the
    exact same comparison can be reproduced later without a live fetch
    (option quotes move constantly, so "live" results aren't reproducible
    on their own).
    """
    snapshot = chain.copy()
    snapshot["spot"] = S
    snapshot["T"] = T
    snapshot["expiry"] = expiry
    snapshot.to_csv(path, index=False)


def load_chain_snapshot(path):
    """Loads a snapshot saved by save_chain_snapshot. Returns (S, T, expiry, chain)."""
    df = pd.read_csv(path)
    S, T, expiry = df["spot"].iloc[0], df["T"].iloc[0], df["expiry"].iloc[0]
    chain = df[["strike", "bid", "ask", "lastPrice", "impliedVolatility"]]
    return S, T, expiry, chain
