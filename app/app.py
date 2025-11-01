import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.simulation_core import simulate_path
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------
# APP TITLE
# --------------------------------------------
st.set_page_config(page_title="Time-Shift AI", layout="centered")
st.title("🕰️ Time-Shift AI — Alternate Futures Simulator")
st.caption("Explore how your decisions today shape different futures")

# --------------------------------------------
# USER INPUTS
# --------------------------------------------
st.sidebar.header("🔧 Simulation Settings")

base_salary = st.sidebar.number_input("Base Salary (AED)", value=10000, step=500)
growth_rate = st.sidebar.slider("Expected Annual Growth Rate", 0.00, 0.30, 0.10)
volatility = st.sidebar.slider("Uncertainty (Volatility)", 0.00, 0.20, 0.05)
risk_tolerance = st.sidebar.slider("Risk Tolerance", 0.0, 2.0, 1.0)
years = st.sidebar.slider("Years to Simulate", 5, 30, 10)

st.sidebar.markdown("---")
st.sidebar.write("💡 Tip: Adjust risk and volatility to see how outcomes diverge.")

# --------------------------------------------
# SIMULATION
# --------------------------------------------
st.subheader("🔮 Predicted Income Trajectories")

np.random.seed(42)
paths = {
    "Stable Path": simulate_path(base_salary, growth_rate, volatility * 0.5, risk_tolerance * 0.8, years, seed=1),
    "Balanced Path": simulate_path(base_salary, growth_rate, volatility, risk_tolerance, years, seed=2),
    "Aggressive Path": simulate_path(base_salary, growth_rate, volatility * 1.5, risk_tolerance * 1.2, years, seed=3)
}

# --------------------------------------------
# PLOT RESULTS
# --------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
for name, vals in paths.items():
    ax.plot(range(1, years + 1), vals, label=name, linewidth=2)
ax.set_title("Career Income Projections (AED)")
ax.set_xlabel("Years Ahead")
ax.set_ylabel("Projected Annual Income")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.5)
st.pyplot(fig)

# --------------------------------------------
# SUMMARY STATS
# --------------------------------------------
st.markdown("### 📊 Summary")
final_incomes = {name: round(vals[-1], 2) for name, vals in paths.items()}
st.write(final_incomes)

best_path = max(final_incomes, key=final_incomes.get)
st.success(f"💫 Highest projected outcome: **{best_path}** — AED {final_incomes[best_path]:,.0f} after {years} years.")

st.caption("Built with ❤️ using Streamlit + NumPy | © Time-Shift AI Prototype")
