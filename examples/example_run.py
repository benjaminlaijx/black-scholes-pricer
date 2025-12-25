from src.black_scholes import call_price, put_price

S = 100
K = 100
r = 0.05
sigma = 0.20
T = 1.0

c = call_price(S, K, r, sigma, T)
p = put_price(S, K, r, sigma, T)

print(f"Call: {c:.2f}")
print(f"Put:  {p:.2f}")
