# black-scholes-pricer
Simple Python implementation of the Black–Scholes option pricing model.

# Black–Scholes Option Pricer

This project implements a simple Python-based Black–Scholes model to price European call and put options.  
It was built to deepen my understanding of option pricing mechanics and how key inputs such as volatility and time to maturity affect option value.

## Features
- Prices European call and put options
- Implements the Black–Scholes closed-form solution
- Clear, modular Python functions
- Example usage with realistic market parameters

## Model Overview
The Black–Scholes model prices options under the following assumptions:
- Constant volatility
- Constant risk-free interest rate
- No dividends
- No transaction costs
- European-style exercise only

The model computes intermediate terms \( d_1 \) and \( d_2 \), which are then used to calculate call and put prices using the standard normal distribution.

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/black-scholes-pricer.git
