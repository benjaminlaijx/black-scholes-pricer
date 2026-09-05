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
python examples/run_backtest.py               # covered-call backtest vs. buy-and-hold
python -m pytest tests/ -v                    # run the test suite
```

`run_backtest.py` pulls live SPY data via `yfinance` by default; use `--csv path/to/prices.csv` to run offline from a local file (`Date` + `Close`/`Adj Close` columns).

## Project Structure
```
src/
  black_scholes.py     # closed-form pricing (d1, d2, call/put price, parity check)
  greeks.py             # delta, gamma, vega, theta, rho
  monte_carlo.py        # GBM simulation used to validate the closed-form solution
  scenario_engine.py    # scenario grid + sensitivity summary
  backtest.py            # covered-call overlay backtest + performance metrics
  data.py                # price history loader (yfinance or local CSV)
examples/               # runnable scripts for each of the above
tests/                   # pytest suite
```

## Limitations
Constant volatility and interest rates, European exercise only, no dividends. The backtest ignores transaction costs, bid/ask spread, and early assignment, and uses trailing realized volatility (not market-implied vol) as the pricing input.
