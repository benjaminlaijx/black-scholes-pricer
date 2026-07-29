"""
Monte Carlo option pricing under geometric Brownian motion.

This exists to validate the closed-form Black-Scholes solution
"from first principles": rather than trusting the analytic d1/d2
formula alone, we simulate the risk-neutral stock price process
directly,

    S_T = S * exp( (r - 0.5*sigma^2)*T + sigma*sqrt(T)*Z ),   Z ~ N(0,1)

discount the average terminal payoff back to today, and compare
against the closed-form price. Agreement (within Monte Carlo
standard error) confirms the analytic implementation is correct.
"""
import numpy as np


def simulate_terminal_prices(S, K, r, sigma, T, n_paths=100_000, seed=None):
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal(n_paths)
    S_T = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
    return S_T


def mc_price(S, K, r, sigma, T, option_type="call", n_paths=100_000, seed=None):
    S_T = simulate_terminal_prices(S, K, r, sigma, T, n_paths, seed)
    if option_type == "call":
        payoffs = np.maximum(S_T - K, 0.0)
    elif option_type == "put":
        payoffs = np.maximum(K - S_T, 0.0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    discounted = np.exp(-r * T) * payoffs
    price = discounted.mean()
    std_err = discounted.std(ddof=1) / np.sqrt(n_paths)
    return price, std_err
