import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import pytest

from src.backtest import realized_vol, run_covered_call_backtest, performance_metrics, max_drawdown


def make_gbm_prices(n=252 * 3, mu=0.08, sigma=0.20, S0=100.0, seed=42):
    rng = np.random.default_rng(seed)
    dt = 1 / 252
    dates = pd.bdate_range("2020-01-02", periods=n)
    log_rets = (mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * rng.standard_normal(n)
    prices = S0 * np.exp(np.cumsum(log_rets))
    return pd.Series(prices, index=dates, name="TEST")


PRICES = make_gbm_prices()


def test_realized_vol_is_positive_and_reasonable():
    vol = realized_vol(PRICES, window=21).dropna()
    assert (vol > 0).all()
    # sanity band: shouldn't wildly diverge from the 20% used to generate the data
    assert vol.mean() == pytest.approx(0.20, abs=0.08)


def test_backtest_returns_expected_columns():
    results = run_covered_call_backtest(PRICES, otm_pct=0.03, hold_days=21, r=0.02)
    assert {"strategy_nav", "benchmark_nav", "premium_pct", "sigma_used"}.issubset(results.columns)
    assert len(results) > 1


def test_backtest_navs_start_at_one():
    results = run_covered_call_backtest(PRICES, otm_pct=0.03, hold_days=21, r=0.02)
    assert results["strategy_nav"].iloc[0] == pytest.approx(1.0)
    assert results["benchmark_nav"].iloc[0] == pytest.approx(1.0)


def test_covered_call_caps_upside_vs_benchmark_in_strong_rally():
    # Steep, low-vol uptrend that blows through the strike each period:
    # benchmark should outrun the capped covered call since premiums
    # (driven by near-zero realized vol here) are too small to compensate.
    dates = pd.bdate_range("2020-01-02", periods=200)
    rally = pd.Series(100.0 * (1.003 ** np.arange(200)), index=dates)
    results = run_covered_call_backtest(rally, otm_pct=0.02, hold_days=21, r=0.02, vol_window=21)
    assert results["benchmark_nav"].iloc[-1] > results["strategy_nav"].iloc[-1]


def test_max_drawdown_is_nonnegative():
    results = run_covered_call_backtest(PRICES, otm_pct=0.03, hold_days=21, r=0.02)
    assert max_drawdown(results["strategy_nav"]) >= 0
    assert max_drawdown(results["benchmark_nav"]) >= 0


def test_performance_metrics_keys():
    results = run_covered_call_backtest(PRICES, otm_pct=0.03, hold_days=21, r=0.02)
    metrics = performance_metrics(results["strategy_nav"], periods_per_year=252 / 21, r=0.02)
    assert set(metrics.keys()) == {
        "CAGR", "annualized_vol", "sharpe_ratio", "max_drawdown", "win_rate", "n_periods"
    }
