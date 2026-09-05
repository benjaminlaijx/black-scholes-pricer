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
- Pricing error stayed under 1% at the money but grew to a mean of ~55% (peaking near 88%) for calls 4-5% out of the money — quantifying the cost of the constant-volatility assumption against the market's actual volatility skew
- This is a live-market snapshot, not a fixed computation — quotes move constantly, so the exact numbers only reproduce from the saved chain snapshot below, not from a fresh live pull
- Reproduce with:
  ```bash
  python examples/run_market_validation.py --csv output/chain_snapshot_2026-10-02.csv
  ```
- Full comparison: `output/market_validation.csv` | Raw chain snapshot: `output/chain_snapshot_2026-10-02.csv`

## Backtest Results: Covered-Call Overlay vs. Buy-and-Hold
- 92 rebalance periods, SPY, 2023–2026, 8-trading-day tenor, 3% OTM, r=2%
- CAGR: 21.6% (strategy) vs. 20.0% (buy-and-hold)
- Sharpe ratio: 1.27 (strategy) vs. 1.13 (buy-and-hold)
- Max drawdown: 17.8% (strategy) vs. 17.3% (buy-and-hold)
- Reproduce with:
  ```bash
  python examples/run_backtest.py --start 2023-01-01 --end 2026-01-01 --hold-days 8
  ```
- Note: these numbers are sensitive to `--hold-days`. At the default 21-day tenor over the same window, the strategy underperforms buy-and-hold on Sharpe (1.08 vs. 1.12) with lower drawdown (16.5% vs. 17.9%) instead — the tenor isn't incidental, it's what determines which of these two results you get.

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
