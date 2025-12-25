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

## Example
For an option with:
- Spot price = 100
- Strike price = 100
- Risk-free rate = 5%
- Volatility = 20%
- Time to maturity = 1 year

The model outputs approximately:
Call price ≈ 10.45
Put price ≈ 5.57

Limitations
- Assumes constant volatility and interest rates
- Supports European options only
- Does not account for dividends
- Not intended for production or live trading use

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/benjaminlaijx/black-scholes-pricer.git
