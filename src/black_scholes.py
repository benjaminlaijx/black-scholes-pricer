"""
Black-Scholes closed-form pricing, vectorized with numpy so it can be
evaluated over arrays of scenarios (not just single scalars).
"""
import numpy as np
from scipy.stats import norm


def d1(S, K, r, sigma, T):
    S, K, r, sigma, T = map(np.asarray, (S, K, r, sigma, T))
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))


def d2(S, K, r, sigma, T):
    return d1(S, K, r, sigma, T) - sigma * np.sqrt(T)


def call_price(S, K, r, sigma, T):
    D1 = d1(S, K, r, sigma, T)
    D2 = d2(S, K, r, sigma, T)
    return S * norm.cdf(D1) - K * np.exp(-r * T) * norm.cdf(D2)


def put_price(S, K, r, sigma, T):
    D1 = d1(S, K, r, sigma, T)
    D2 = d2(S, K, r, sigma, T)
    return K * np.exp(-r * T) * norm.cdf(-D2) - S * norm.cdf(-D1)


def put_call_parity_check(S, K, r, sigma, T, tol=1e-8):
    C = call_price(S, K, r, sigma, T)
    P = put_price(S, K, r, sigma, T)
    lhs = C - P
    rhs = S - K * np.exp(-r * T)
    return np.all(np.abs(lhs - rhs) < tol)

