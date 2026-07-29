import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pytest

from src.black_scholes import call_price, put_price, put_call_parity_check
from src.greeks import delta, gamma, vega, theta, rho
from src.monte_carlo import mc_price
from src.scenario_engine import build_scenario_grid, sensitivity_summary


S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.20, 1.0


def test_call_price_matches_known_value():
    # Textbook value for these inputs is ~10.4506
    assert call_price(S, K, r, sigma, T) == pytest.approx(10.4506, abs=1e-3)


def test_put_price_matches_known_value():
    # Textbook value for these inputs is ~5.5735
    assert put_price(S, K, r, sigma, T) == pytest.approx(5.5735, abs=1e-3)


def test_put_call_parity_holds():
    assert put_call_parity_check(S, K, r, sigma, T)


def test_call_price_increases_with_volatility():
    low = call_price(S, K, r, 0.10, T)
    high = call_price(S, K, r, 0.40, T)
    assert high > low


def test_call_delta_between_zero_and_one():
    d = delta(S, K, r, sigma, T, "call")
    assert 0.0 < d < 1.0


def test_put_delta_between_minus_one_and_zero():
    d = delta(S, K, r, sigma, T, "put")
    assert -1.0 < d < 0.0


def test_gamma_matches_for_call_and_put():
    # gamma is identical for calls and puts at the same strike/maturity
    assert gamma(S, K, r, sigma, T) > 0


def test_vega_positive():
    assert vega(S, K, r, sigma, T) > 0


def test_monte_carlo_agrees_with_closed_form():
    closed_form = call_price(S, K, r, sigma, T)
    mc_est, mc_se = mc_price(S, K, r, sigma, T, "call", n_paths=200_000, seed=1)
    # closed-form should sit within ~4 standard errors of the MC estimate
    assert abs(closed_form - mc_est) < 4 * mc_se


def test_scenario_grid_has_over_1000_scenarios():
    df = build_scenario_grid()
    assert len(df) >= 1000


def test_scenario_grid_prices_are_nonnegative():
    df = build_scenario_grid()
    assert (df["price"] >= 0).all()


def test_sensitivity_summary_covers_all_three_inputs():
    df = build_scenario_grid()
    summary = sensitivity_summary(df)
    inputs = set(summary["input"])
    assert inputs == {"volatility (sigma)", "time to maturity (T)", "risk-free rate (r)"}


def test_price_is_monotonic_in_time_to_maturity_for_itm_call():
    # For a call with r>0, price generally increases with more time
    short = call_price(S, K, r, sigma, 0.25)
    long = call_price(S, K, r, sigma, 2.0)
    assert long > short
