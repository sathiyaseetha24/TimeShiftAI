import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.simulation_core import simulate_path

st.set_page_config(page_title="Time-Shift AI", page_icon="⏳", layout="centered")

st.title("⏳ Time-Shift AI — Career Future Simulator")
st.markdown("Visualize how your career path could evolve across alternate futures!")

# --- User Inputs ---
st.sidebar.header("Scenario Settings")
career = st.sidebar.selectbox("Career Path", ["Stay in Job", "Join Startup", "Go Freelance"])
base_salary = st.sidebar.number_input("Current Annual Income (AED)", 20000, 1000000, 120000)
risk_tolerance = st.sidebar.slider("Risk Tolerance", 0.0, 1.0, 0.5)
growth_focus = st.sidebar.slider("Career Growth Focus", 0.0, 1.0, 0.7)
years = st.sidebar.slider("Years to Simulate", 5, 20, 10)

# --- Model Parameters by Career Type ---
career_profiles = {
    "Stay in Job": dict(growth_rate=0.05, volatility=0.02),
    "Join Startup": dict(growth_rate=0.12, volatility=0.15),
    "Go Freelance": dict(growth_rate=0.08, volatility=0.1)
}

profile = career_profiles[career]
salaries = simulate_path(base_salary, profile["growth_rate"], profile["volatility"], risk_tolerance, years)

# --- Visualization ---
st.subheader(f"Projected Income Path ({career})")
df = pd.DataFrame({"Year": range(1, years + 1), "Predicted Income": salaries})
st.line_chart(df.set_index("Year"))

# --- Summary ---
st.metric("Final Year Projection", f"AED {salaries[-1]:,.0f}")
st.success(f"💡 This scenario suggests a potential **{(salaries[-1]/base_salary - 1)*100:.1f}%** income change over {years} years.")
