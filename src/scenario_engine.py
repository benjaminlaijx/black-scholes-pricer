"""
Scenario engine: builds a grid of (sigma, T, r) combinations, prices a
European option under each combination, and attaches the analytic
Greeks -- this is the "run 1,000+ simulated scenarios to quantify
price sensitivity to volatility, time to maturity, and interest rates"
piece.
"""
import numpy as np
import pandas as pd

from .black_scholes import call_price, put_price
from .greeks import vega, theta, rho


def build_scenario_grid(
    S=100.0,
    K=100.0,
    sigma_range=(0.05, 0.60, 20),   # (low, high, n_points)
    T_range=(0.05, 2.00, 10),
    r_range=(0.00, 0.10, 6),
    option_type="call",
):
    """
    Cartesian product of sigma x T x r -> one row per scenario.
    Default grid = 20 * 10 * 6 = 1,200 scenarios (>1,000).
    """
    sigmas = np.linspace(*sigma_range)
    Ts = np.linspace(*T_range)
    rs = np.linspace(*r_range)

    grid_sigma, grid_T, grid_r = np.meshgrid(sigmas, Ts, rs, indexing="ij")
    grid_sigma = grid_sigma.ravel()
    grid_T = grid_T.ravel()
    grid_r = grid_r.ravel()

    price_fn = call_price if option_type == "call" else put_price
    prices = price_fn(S, K, grid_r, grid_sigma, grid_T)

    df = pd.DataFrame({
        "S": S,
        "K": K,
        "sigma": grid_sigma,
        "T": grid_T,
        "r": grid_r,
        "price": prices,
        "vega": vega(S, K, grid_r, grid_sigma, grid_T),
        "theta": theta(S, K, grid_r, grid_sigma, grid_T, option_type),
        "rho": rho(S, K, grid_r, grid_sigma, grid_T, option_type),
    })
    df.attrs["option_type"] = option_type
    df.attrs["S"] = S
    df.attrs["K"] = K
    return df


def sensitivity_summary(df):
    """
    Quantify sensitivity as: how much does price move, on average and
    at the extreme, per unit move in each input, holding the others at
    their grid midpoints. Returns a tidy summary DataFrame.
    """
    S, K = df.attrs["S"], df.attrs["K"]
    # Use the middle element of each unique, sorted axis (not np.median,
    # which can average two middle values that don't actually appear in
    # the grid when the axis has an even length).
    mid_T = np.sort(df["T"].unique())[len(df["T"].unique()) // 2]
    mid_r = np.sort(df["r"].unique())[len(df["r"].unique()) // 2]
    mid_sigma = np.sort(df["sigma"].unique())[len(df["sigma"].unique()) // 2]

    rows = []

    # Sensitivity to sigma (holding T, r at medians)
    slice_sigma = df[np.isclose(df["T"], mid_T) & np.isclose(df["r"], mid_r)].sort_values("sigma")
    d_price = np.gradient(slice_sigma["price"], slice_sigma["sigma"])
    rows.append({
        "input": "volatility (sigma)",
        "price_range": slice_sigma["price"].max() - slice_sigma["price"].min(),
        "avg_sensitivity_per_unit": np.mean(d_price),
        "max_sensitivity_per_unit": np.max(np.abs(d_price)),
    })

    # Sensitivity to T (holding sigma, r at medians)
    slice_T = df[np.isclose(df["sigma"], mid_sigma) & np.isclose(df["r"], mid_r)].sort_values("T")
    d_price = np.gradient(slice_T["price"], slice_T["T"])
    rows.append({
        "input": "time to maturity (T)",
        "price_range": slice_T["price"].max() - slice_T["price"].min(),
        "avg_sensitivity_per_unit": np.mean(d_price),
        "max_sensitivity_per_unit": np.max(np.abs(d_price)),
    })

    # Sensitivity to r (holding sigma, T at medians)
    slice_r = df[np.isclose(df["sigma"], mid_sigma) & np.isclose(df["T"], mid_T)].sort_values("r")
    d_price = np.gradient(slice_r["price"], slice_r["r"])
    rows.append({
        "input": "risk-free rate (r)",
        "price_range": slice_r["price"].max() - slice_r["price"].min(),
        "avg_sensitivity_per_unit": np.mean(d_price),
        "max_sensitivity_per_unit": np.max(np.abs(d_price)),
    })

    return pd.DataFrame(rows)
