"""
Analytic Black-Scholes Greeks: the closed-form partial derivatives that
quantify option price sensitivity to each input.

    delta = dPrice/dS      vega  = dPrice/dsigma   (per 1.00 vol, i.e. 100 vol pts)
    gamma = d^2Price/dS^2  theta = dPrice/dT        (per year; also per-day below)
    rho   = dPrice/dr

All functions are vectorized (numpy) so they can be evaluated over whole
grids of scenarios at once.
"""
import numpy as np
from scipy.stats import norm
from .black_scholes import d1, d2


def delta(S, K, r, sigma, T, option_type="call"):
    D1 = d1(S, K, r, sigma, T)
    if option_type == "call":
        return norm.cdf(D1)
    elif option_type == "put":
        return norm.cdf(D1) - 1
    raise ValueError("option_type must be 'call' or 'put'")


def gamma(S, K, r, sigma, T):
    D1 = d1(S, K, r, sigma, T)
    return norm.pdf(D1) / (S * sigma * np.sqrt(T))


def vega(S, K, r, sigma, T):
    """Price change per 1.00 (100 percentage points) change in volatility."""
    D1 = d1(S, K, r, sigma, T)
    return S * norm.pdf(D1) * np.sqrt(T)


def theta(S, K, r, sigma, T, option_type="call", per_day=False):
    D1 = d1(S, K, r, sigma, T)
    D2 = d2(S, K, r, sigma, T)
    term1 = -(S * norm.pdf(D1) * sigma) / (2 * np.sqrt(T))
    if option_type == "call":
        term2 = -r * K * np.exp(-r * T) * norm.cdf(D2)
        th = term1 + term2
    elif option_type == "put":
        term2 = r * K * np.exp(-r * T) * norm.cdf(-D2)
        th = term1 + term2
    else:
        raise ValueError("option_type must be 'call' or 'put'")
    return th / 365.0 if per_day else th


def rho(S, K, r, sigma, T, option_type="call"):
    D2 = d2(S, K, r, sigma, T)
    if option_type == "call":
        return K * T * np.exp(-r * T) * norm.cdf(D2)
    elif option_type == "put":
        return -K * T * np.exp(-r * T) * norm.cdf(-D2)
    raise ValueError("option_type must be 'call' or 'put'")


def all_greeks(S, K, r, sigma, T, option_type="call"):
    return {
        "delta": delta(S, K, r, sigma, T, option_type),
        "gamma": gamma(S, K, r, sigma, T),
        "vega": vega(S, K, r, sigma, T),
        "theta": theta(S, K, r, sigma, T, option_type),
        "rho": rho(S, K, r, sigma, T, option_type),
    }
