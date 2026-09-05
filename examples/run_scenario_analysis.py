"""
Runs 1,000+ scenarios across volatility, time to maturity, and the
risk-free rate; quantifies price sensitivity to each; validates the
closed-form pricer against a Monte Carlo simulation; and saves plots.

Usage:
    python examples/run_scenario_analysis.py
"""
import os
import sys
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.black_scholes import call_price, put_call_parity_check
from src.scenario_engine import build_scenario_grid, sensitivity_summary
from src.monte_carlo import mc_price

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    S, K = 100.0, 100.0

    df = build_scenario_grid(S=S, K=K, option_type="call")
    print(f"Ran {len(df):,} scenarios across sigma x T x r.\n")

    summary = sensitivity_summary(df)
    print("Sensitivity summary (holding other inputs at grid medians):")
    print(summary.to_string(index=False))
    print()

    # Validate the closed-form pricer against an independent Monte Carlo simulation
    base_sigma, base_T, base_r = 0.20, 1.0, 0.05
    closed_form = call_price(S, K, base_r, base_sigma, base_T)
    mc_est, mc_se = mc_price(S, K, base_r, base_sigma, base_T,
                              option_type="call", n_paths=200_000, seed=42)
    print("Validation vs. Monte Carlo simulation (S=K=100, sigma=20%, T=1, r=5%):")
    print(f"  Closed-form price: {closed_form:.4f}")
    print(f"  Monte Carlo price: {mc_est:.4f}  (+/- {1.96*mc_se:.4f} 95% CI)")
    print(f"  Difference:        {abs(closed_form - mc_est):.4f}")
    print(f"  Put-call parity holds: {put_call_parity_check(S, K, base_r, base_sigma, base_T)}")
    print()

    mid_T = df["T"].unique()[len(df["T"].unique()) // 2]
    mid_r = df["r"].unique()[len(df["r"].unique()) // 2]
    mid_sigma = df["sigma"].unique()[len(df["sigma"].unique()) // 2]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    s1 = df[(df["T"].round(4) == round(mid_T, 4)) & (df["r"].round(4) == round(mid_r, 4))].sort_values("sigma")
    axes[0].plot(s1["sigma"] * 100, s1["price"])
    axes[0].set_xlabel("Volatility (%)")
    axes[0].set_ylabel("Call price")
    axes[0].set_title(f"Price vs. Volatility\n(T={mid_T:.2f}y, r={mid_r:.1%})")

    s2 = df[(df["sigma"].round(4) == round(mid_sigma, 4)) & (df["r"].round(4) == round(mid_r, 4))].sort_values("T")
    axes[1].plot(s2["T"], s2["price"], color="darkorange")
    axes[1].set_xlabel("Time to maturity (years)")
    axes[1].set_ylabel("Call price")
    axes[1].set_title(f"Price vs. Time to Maturity\n(sigma={mid_sigma:.0%}, r={mid_r:.1%})")

    s3 = df[(df["sigma"].round(4) == round(mid_sigma, 4)) & (df["T"].round(4) == round(mid_T, 4))].sort_values("r")
    axes[2].plot(s3["r"] * 100, s3["price"], color="green")
    axes[2].set_xlabel("Risk-free rate (%)")
    axes[2].set_ylabel("Call price")
    axes[2].set_title(f"Price vs. Interest Rate\n(sigma={mid_sigma:.0%}, T={mid_T:.2f}y)")

    plt.tight_layout()
    plot_path = os.path.join(OUT_DIR, "sensitivity_curves.png")
    plt.savefig(plot_path, dpi=150)
    print(f"Saved sensitivity plots to {plot_path}")

    csv_path = os.path.join(OUT_DIR, "scenario_grid.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved full scenario grid ({len(df):,} rows) to {csv_path}")


if __name__ == "__main__":
    main()
