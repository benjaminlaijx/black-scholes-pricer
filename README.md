# Black-Scholes Option Pricer

Closed-form Black-Scholes engine for European options, built from first principles (no pricing libraries), with a scenario/sensitivity framework, Monte Carlo validation, and a backtested trading strategy on top of it.

## Overview
- Closed-form pricing and analytic Greeks (delta, gamma, vega, theta, rho), vectorized with numpy
- Scenario engine pricing a 1,200-point grid across volatility, time to maturity, and interest rate, with a sensitivity summary per input
- Closed-form prices validated against a 200,000-path Monte Carlo simulation (agree to within $0.01) and a put-call parity check
- Covered-call overlay strategy backtested on SPY against buy-and-hold, reporting CAGR, Sharpe ratio, max drawdown, and win rate
- 19 unit tests covering pricing accuracy, Greeks, parity, Monte Carlo agreement, and backtest mechanics

## Quick Start
```bash
git clone https://github.com/benjaminlaijx/black-scholes-pricer.git
cd black-scholes-pricer
pip install -r requirements.txt
```

## Usage
```bash
python examples/example_run.py               # price a single option
python examples/run_scenario_analysis.py      # 1,200-scenario grid + sensitivity + MC validation
python examples/run_market_validation.py      # benchmark against live SPY option quotes
python examples/run_backtest.py               # covered-call backtest vs. buy-and-hold
python -m pytest tests/ -v                    # run the test suite
```

`run_backtest.py` pulls live SPY data via `yfinance` by default; use `--csv path/to/prices.csv` to run offline from a local file (`Date` + `Close`/`Adj Close` columns).

## Market Validation
- Benchmarked closed-form prices against a live SPY option chain, using a single ATM implied vol as sigma across every strike (OTM calls only, >=25 days to expiry, quotes below $0.10 excluded)
- Pricing error was ~4% within 1% of the money, rose to a mean of ~83% (peaking near 88%) for calls 4-5% out of the money, and averaged ~56% across all strikes more than 2% OTM — quantifying the cost of the constant-volatility assumption against the market's actual volatility skew
- This is a live-market snapshot, not a fixed computation — quotes move constantly, so the exact numbers only reproduce from the saved chain snapshot below, not from a fresh live pull
- Reproduce with:
  ```bash
  python examples/run_market_validation.py --csv output/chain_snapshot_2026-10-02.csv
  ```
- Full comparison: `output/market_validation.csv` | Raw chain snapshot: `output/chain_snapshot_2026-10-02.csv`

## Backtest Results: Covered-Call Overlay vs. Buy-and-Hold
SPY daily closes, 2023-01-03 to 2025-12-31 (unadjusted close, no dividend reinvestment), 3% OTM, r=2%.

| Tenor | Periods | CAGR (strategy) | CAGR (B&H) | Sharpe (strategy) | Sharpe (B&H) | Max DD (strategy) | Max DD (B&H) |
|---|---|---|---|---|---|---|---|
| 8-day  | 92 | 20.1% | 18.4% | 1.19 | 1.05 | 17.8% | 17.6% |
| 21-day | 35 | 14.7% | 18.4% | 1.00 | 1.03 | 16.8% | 18.3% |

The overlay beats buy-and-hold on both CAGR and Sharpe at an 8-day tenor, but *loses* on both at the default 21-day tenor — tenor isn't incidental, it's what determines which of these two results you get.

These numbers use unadjusted closing prices, so buy-and-hold CAGR is understated relative to a total-return series (no dividends reinvested); the strategy side is affected less since much of its return comes from premium income rather than price appreciation. Numbers will differ slightly with an adjusted-close source (e.g. `yfinance` with `auto_adjust=True`).
- Reproduce with:
  ```bash
  python examples/run_backtest.py --csv output/spy_prices_2023_2026.csv --start 2023-01-01 --end 2026-01-01 --hold-days 8
  python examples/run_backtest.py --csv output/spy_prices_2023_2026.csv --start 2023-01-01 --end 2026-01-01 --hold-days 21
  ```
- Price data: `output/spy_prices_2023_2026.csv` | Saved period-by-period results (8-day run): `output/backtest_results.csv`

## Project Structure
```
src/
  black_scholes.py     # closed-form pricing (d1, d2, call/put price, parity check)
  greeks.py             # delta, gamma, vega, theta, rho
  monte_carlo.py        # GBM simulation used to validate the closed-form solution
  scenario_engine.py    # scenario grid + sensitivity summary
  market_validation.py   # live SPY option chain fetch + comparison vs. closed-form
  backtest.py            # covered-call overlay backtest + performance metrics
  data.py                # price history loader (yfinance or local CSV)
examples/               # runnable scripts for each of the above
tests/                   # pytest suite
```

## Limitations
Constant volatility and interest rates, European exercise only, no dividends. The backtest ignores transaction costs, bid/ask spread, and early assignment, and uses trailing realized volatility (not market-implied vol) as the pricing input.
