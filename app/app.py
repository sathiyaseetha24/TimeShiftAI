# app/app.py
import requests
import streamlit as st
import pandas as pd
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TimeShiftAI — Future Decision Lab",
    page_icon="🕰️",
    layout="wide"
)

# ---------------- CSS FIXES ----------------
st.markdown("""
    <style>
        /* Hide sidebar arrow and sidebar area */
        [data-testid="collapsedControl"], [data-testid="stSidebar"] {
            display: none !important;
            visibility: hidden !important;
        }
        /* Hide stray text like 'keyboard_double_arrow_right' */
        span:contains("keyboard_double_arrow_right") {
            display: none !important;
        }

        * { font-family: 'Segoe UI', sans-serif !important; }
        h1 { color: #1E88E5; font-weight: 700; }
        h2, h3, h4, h5, h6 { color: #1565C0; font-weight: 600; }

        .stMetric {
            background-color: #F5F9FF;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1rem;
            max-width: 1100px;
            margin: auto;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🕰️ TimeShiftAI — The Future Decision Lab")
st.markdown("""
### 🌍 Simulate, Compare, and Visualize Your Possible Tomorrows  
Discover how your **career choices**, **risk tolerance**, and **financial lifestyle** influence your future wealth and happiness.
""")

# ---------------- USER INPUT SECTION ----------------
st.markdown("#### ⚙️ Configure Your Profile and Simulation")

colA, colB, colC = st.columns(3)
with colA:
    currency = st.selectbox("Preferred Currency 💱", ["AED", "USD", "INR", "EUR", "GBP"])
    salary = st.number_input(f"Current Monthly Salary ({currency})", value=15000)
with colB:
    family_expense = st.number_input(f"Monthly Family Expense ({currency})", value=5000)
    emi = st.number_input(f"Total Monthly EMIs ({currency})", value=2000)
with colC:
    savings = st.number_input(f"Current Savings ({currency})", value=10000)
    risk_tolerance = st.slider("Risk Appetite (0 = Low, 10 = High)", 0, 10, 5)

colD, colE = st.columns(2)
with colD:
    years = st.slider("Years to Simulate", 1, 20, 10)
with colE:
    growth_bias = st.slider("Market Growth Bias (%)", 0, 15, 5)

# ---------------- CURRENCY HANDLING ----------------
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

# ---------------- RESULTS VISUALIZATION ----------------
st.markdown("---")
st.markdown("### 📈 Simulation Results")

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
    happiness = {
        "Stay in Job": np.random.uniform(6, 8),
        "Go Freelance": np.random.uniform(7, 9),
        "Join Startup": np.random.uniform(4, 7)
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
