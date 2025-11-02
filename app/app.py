# app/app.py
import requests
import streamlit as st
import pandas as pd
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TimeShiftAI — Future Decision Lab",
    page_icon="🕰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CSS FIXES ----------------
st.markdown("""
    <style>
        /* Hide Streamlit sidebar collapse/expand button */
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        /* General UI styling */
        * { font-family: 'Segoe UI', sans-serif !important; }
        h1 { color: #1E88E5; font-weight: 700; }
        h2, h3, h4, h5, h6 { color: #1565C0; font-weight: 600; }

        .stMetric {
            background-color: #F5F9FF;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        }

        .stMetricLabel {
            color: #333 !important;
            font-size: 16px !important;
        }

        .stMetricValue {
            color: #1E88E5 !important;
            font-size: 22px !important;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🕰️ TimeShiftAI — The Future Decision Lab")
st.markdown("""
### 🌍 Simulate, Compare, and Visualize Your Possible Tomorrows  
Discover how your **career choices**, **risk tolerance**, and **financial lifestyle** influence your future wealth and happiness.
""")

# ---------------- SIDEBAR INPUTS ----------------
st.sidebar.header("🎯 Your Current Profile")

currency = st.sidebar.selectbox("Preferred Currency 💱", ["AED", "USD", "INR", "EUR", "GBP"])

# --- Currency Conversion ---
base_currency = "AED"
conversion_rate = 1.0

if currency != base_currency:
    try:
        response = requests.get(f"https://api.exchangerate.host/latest?base={base_currency}&symbols={currency}")
        if response.status_code == 200:
            data = response.json()
            conversion_rate = data["rates"][currency]
        else:
            st.warning("⚠️ Currency conversion API unavailable, showing values in AED.")
    except Exception:
        st.warning("⚠️ Could not fetch currency rates. Using AED values.")

# --- Financial Inputs ---
salary = st.sidebar.number_input(f"Current Monthly Salary ({currency})", value=15000)
family_expense = st.sidebar.number_input(f"Monthly Family Expense ({currency})", value=5000)
emi = st.sidebar.number_input(f"Total Monthly EMIs ({currency})", value=2000)
savings = st.sidebar.number_input(f"Current Savings ({currency})", value=10000)
risk_tolerance = st.sidebar.slider("Risk Appetite (0 = Low, 10 = High)", 0, 10, 5)
years = st.sidebar.slider("Years to Simulate", 1, 20, 10)
growth_bias = st.sidebar.slider("Market Growth Bias (%)", 0, 15, 5)

# ---------------- SCENARIO DEFINITIONS ----------------
scenarios = {
    "Stay in Job": {"growth": 0.05 + growth_bias / 100, "volatility": 0.02},
    "Join Startup": {"growth": 0.12 + growth_bias / 100, "volatility": 0.08},
    "Go Freelance": {"growth": 0.08 + growth_bias / 100, "volatility": 0.05},
}

# ---------------- SIMULATION LOGIC ----------------
data = []
for scenario, vals in scenarios.items():
    incomes = [salary * 12]
    wealth = [savings]
    for year in range(1, years + 1):
        income = incomes[-1] * (1 + np.random.normal(vals["growth"], vals["volatility"]))
        yearly_expense = (family_expense + emi) * 12
        net = wealth[-1] + income - yearly_expense
        incomes.append(income)
        wealth.append(net)
    df = pd.DataFrame({"Year": range(0, years + 1), "Wealth": wealth})
    df["Scenario"] = scenario
    data.append(df)

df_all = pd.concat(data)

# ---------------- MAIN LAYOUT ----------------
col1, col2 = st.columns([1.7, 1])

with col1:
    st.subheader(f"💰 Projected Wealth Over {years} Years ({currency})")
    converted_df = df_all.copy()
    converted_df["Wealth"] = converted_df["Wealth"] * conversion_rate
    st.line_chart(
        converted_df.pivot(index="Year", columns="Scenario", values="Wealth"),
        height=420
    )

with col2:
    st.subheader("📊 Snapshot Insights")

    last_values = df_all[df_all["Year"] == years][["Scenario", "Wealth"]].reset_index(drop=True)

    best_row = last_values.loc[last_values["Wealth"].idxmax()]
    worst_row = last_values.loc[last_values["Wealth"].idxmin()]

    best_wealth = float(best_row["Wealth"]) * conversion_rate
    worst_wealth = float(worst_row["Wealth"]) * conversion_rate

    st.metric("💹 Best Financial Path", best_row["Scenario"], f"{best_wealth:,.0f} {currency}")
    st.metric("⚠️ Lowest Return Path", worst_row["Scenario"], f"{worst_wealth:,.0f} {currency}")

    # --- Simulated Happiness Metrics ---
    job_satisfaction = np.random.uniform(6, 8)
    freelance_freedom = np.random.uniform(7, 9)
    startup_pressure = np.random.uniform(4, 7)

    happiness = {
        "Stay in Job": job_satisfaction,
        "Go Freelance": freelance_freedom,
        "Join Startup": startup_pressure
    }

    h_df = pd.DataFrame.from_dict(happiness, orient='index', columns=['Happiness Score'])
    st.bar_chart(h_df)

# ---------------- FINAL INSIGHT ----------------
st.markdown("---")
st.subheader("💡 Decision Intelligence Summary")

if risk_tolerance <= 3:
    st.info("Your low risk appetite fits a **stable job** with consistent income growth.")
elif 4 <= risk_tolerance <= 7:
    st.info("You can balance between **freelancing** and **startup exploration** with calculated safety nets.")
else:
    st.success("Your high-risk appetite fits **startup ventures** or **freelancing**, where potential returns outweigh risks!")

st.caption("🧠 Tip: Adjust EMIs, family expense, and growth bias sliders to explore how your wealth path shifts in real-time.")
