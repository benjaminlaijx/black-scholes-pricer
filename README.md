# Black–Scholes Option Pricer

A Python implementation of the Black–Scholes model for pricing European call and put options, built from first principles (closed-form d1/d2 derivation, no pricing libraries). It includes a scenario engine that prices options across 1,200+ combinations of volatility, time to maturity, and interest rate, computes the analytic Greeks, and validates the closed-form solution against an independent Monte Carlo simulation.

## Features
- Closed-form Black–Scholes pricing for European calls and puts, vectorized with numpy
- Analytic Greeks: delta, gamma, vega, theta, rho
- Scenario engine: prices a 20 × 10 × 6 grid (1,200 scenarios) across volatility, time to maturity, and interest rate
- Sensitivity analysis quantifying average and peak price sensitivity to each input
- Monte Carlo simulation (geometric Brownian motion) used as an independent check on the closed-form prices, plus a put-call parity check
- Matplotlib sensitivity curves and a CSV export of the full scenario grid
- Unit tests (pytest) covering pricing accuracy, Greeks, parity, and Monte Carlo agreement

## Model Overview
The Black–Scholes model prices options under these assumptions:
- Constant volatility and risk-free rate
- No dividends, no transaction costs
- European-style exercise only

The model computes intermediate terms d1 and d2, used with the standard normal CDF to price calls and puts. The Greeks (delta, gamma, vega, theta, rho) are the partial derivatives of price with respect to each input — this is what "sensitivity" means quantitatively, and what the scenario engine measures empirically across the grid.

## Quick Example
For S = K = 100, r = 5%, sigma = 20%, T = 1 year:
- Call price ≈ 10.45
- Put price ≈ 5.57

```bash
python examples/example_run.py
```

## Scenario / Sensitivity Analysis
```bash
python examples/run_scenario_analysis.py
```
This runs 1,200 scenarios across sigma ∈ [5%, 60%], T ∈ [0.05, 2] years, and r ∈ [0%, 10%]; prints a sensitivity summary; validates the closed-form price against a 200,000-path Monte Carlo simulation; and saves:
- `output/sensitivity_curves.png` — price vs. each input, holding the others fixed
- `output/scenario_grid.csv` — the full 1,200-row scenario grid with price and Greeks

Sample output:
```
Ran 1,200 scenarios across sigma x T x r.

Sensitivity summary (holding other inputs at grid medians):
               input  price_range  avg_sensitivity_per_unit  max_sensitivity_per_unit
  volatility (sigma)        20.83                     37.57                     39.67
time to maturity (T)        20.92                     11.07                     21.12
  risk-free rate (r)         5.24                     52.41                     55.31

Validation vs. Monte Carlo simulation (S=K=100, sigma=20%, T=1, r=5%):
  Closed-form price: 10.4506
  Monte Carlo price: 10.4634  (+/- 0.0649 95% CI)
  Put-call parity holds: True
```

## Tests
```bash
python -m pytest tests/ -v
```
13 tests covering: pricing accuracy against known values, put-call parity, Greeks bounds, Monte Carlo agreement with the closed-form solution, and scenario grid integrity.

## Project Structure
```
src/
  black_scholes.py     # closed-form pricing (d1, d2, call/put price, parity check)
  greeks.py             # delta, gamma, vega, theta, rho
  monte_carlo.py        # GBM simulation used to validate the closed-form solution
  scenario_engine.py    # builds the scenario grid + sensitivity summary
examples/
  example_run.py            # single-scenario pricing
  run_scenario_analysis.py  # full 1,200-scenario sensitivity analysis + plots
tests/
  test_black_scholes.py
```

## Limitations
- Assumes constant volatility and interest rates
- Supports European options only
- Does not account for dividends
- Not intended for production or live trading use

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/benjaminlaijx/black-scholes-pricer.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the example script:
   ```bash
   python examples/example_run.py
   ```
4. Run the full scenario/sensitivity analysis:
   ```bash
   python examples/run_scenario_analysis.py
   ```
