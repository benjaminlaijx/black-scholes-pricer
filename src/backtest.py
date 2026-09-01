"""
Backtest: a systematic covered-call overlay on top of a long stock
position, priced with this repo's own Black-Scholes engine.

Strategy, rebalanced every `hold_days` trading days:
  1. Start fully invested in the underlying.
  2. Sell one at-the-money-plus-x% call per share held, struck at
     K = S_start * (1 + otm_pct), maturing in `hold_days` trading days.
     The premium is priced with this repo's `call_price()` -- not
     pulled from the market -- using trailing realized volatility as
     the sigma input, since that's the only volatility estimate we
     can compute purely from price history.
  3. Hold to expiry. Payoff per share is min(S_end, K) - i.e. upside
     is capped at the strike, exactly like a real covered call -- plus
     the premium collected up front.
  4. Reinvest fully in the stock and repeat.

This is deliberately simple (no bid/ask, no early assignment, no
transaction costs, single fixed OTM% and tenor). That's a feature for
a resume project, not a bug: state the assumptions plainly and let the
Sharpe/drawdown numbers speak for themselves.

A buy-and-hold benchmark is computed over the same period for
comparison, which is the honest way to show whether the overlay
actually helped.
"""
import numpy as np
import pandas as pd

from .black_scholes import call_price


def realized_vol(prices, window=21, trading_days=252):
    """
    Annualized realized volatility from trailing daily log returns.
    Uses only data up to and including each date (no lookahead) --
    the value at date t is computed from returns in (t-window, t].
    """
    log_ret = np.log(prices / prices.shift(1))
    return log_ret.rolling(window).std() * np.sqrt(trading_days)


def run_covered_call_backtest(
    prices,
    otm_pct=0.03,
    hold_days=21,
    r=0.02,
    vol_window=21,
    trading_days=252,
):
    """
    Parameters
    ----------
    prices : pd.Series of daily close prices, indexed by date.
    otm_pct : how far out-of-the-money the sold call is struck, e.g.
        0.03 = strike is 3% above spot at the start of each period.
    hold_days : trading days between rebalances (and the option's
        tenor, since it's sold at the start of a period and held to
        expiry at the end of it).
    r : annualized risk-free rate used both to price the option and
        as the Sharpe ratio's risk-free rate.
    vol_window : trailing window (trading days) used to estimate the
        realized volatility fed into Black-Scholes as sigma.

    Returns
    -------
    pd.DataFrame indexed by rebalance date with columns:
        strategy_nav, benchmark_nav, premium_pct, sigma_used
    """
    vol = realized_vol(prices, window=vol_window, trading_days=trading_days)

    # First tradeable date needs `vol_window` days of history behind it.
    start_idx = vol.first_valid_index()
    prices = prices.loc[start_idx:]
    vol = vol.loc[start_idx:]

    rebalance_idx = list(range(0, len(prices) - 1, hold_days))
    T = hold_days / trading_days

    strategy_nav = [1.0]      # normalized to start at 1.0
    benchmark_nav = [1.0]
    dates = [prices.index[0]]
    premiums_pct = []
    sigmas_used = []

    for i in rebalance_idx:
        j = min(i + hold_days, len(prices) - 1)
        if i == j:
            break

        S_start = prices.iloc[i]
        S_end = prices.iloc[j]
        sigma = vol.iloc[i]
        if not np.isfinite(sigma) or sigma <= 0:
            sigma = vol.dropna().iloc[0]  # fallback: earliest available estimate

        K = S_start * (1 + otm_pct)
        premium = call_price(S_start, K, r, sigma, T)
        premium_pct = premium / S_start  # premium as a % of capital deployed

        # Covered call payoff per dollar invested: capped upside + premium.
        capped_return = min(S_end, K) / S_start
        strategy_period_return = capped_return + premium_pct

        # Buy-and-hold benchmark over the same period.
        benchmark_period_return = S_end / S_start

        strategy_nav.append(strategy_nav[-1] * strategy_period_return)
        benchmark_nav.append(benchmark_nav[-1] * benchmark_period_return)
        dates.append(prices.index[j])
        premiums_pct.append(premium_pct)
        sigmas_used.append(sigma)

    df = pd.DataFrame({
        "strategy_nav": strategy_nav,
        "benchmark_nav": benchmark_nav,
    }, index=pd.DatetimeIndex(dates, name="date"))

    # Per-period diagnostics, one row shorter than the NAV series.
    df["premium_pct"] = [np.nan] + premiums_pct
    df["sigma_used"] = [np.nan] + sigmas_used

    return df


def max_drawdown(nav):
    """Largest peak-to-trough decline in a NAV series, as a positive fraction."""
    running_max = nav.cummax()
    drawdown = (nav - running_max) / running_max
    return -drawdown.min()


def performance_metrics(nav, periods_per_year, r=0.02):
    """
    Computes CAGR, annualized volatility, Sharpe ratio, max drawdown,
    and per-period win rate from a NAV series (starting at any level;
    only relative changes matter).
    """
    period_returns = nav.pct_change().dropna()
    n_periods = len(period_returns)
    years = n_periods / periods_per_year

    total_return = nav.iloc[-1] / nav.iloc[0]
    cagr = total_return ** (1 / years) - 1 if years > 0 else np.nan

    ann_vol = period_returns.std() * np.sqrt(periods_per_year)
    ann_mean_return = period_returns.mean() * periods_per_year
    sharpe = (ann_mean_return - r) / ann_vol if ann_vol > 0 else np.nan

    return {
        "CAGR": cagr,
        "annualized_vol": ann_vol,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown(nav),
        "win_rate": (period_returns > 0).mean(),
        "n_periods": n_periods,
    }
