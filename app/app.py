# app/app.py
import streamlit as st
import pandas as pd
import numpy as np
import requests
from collections import deque

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="TimeShiftAI — Future Decision Lab", page_icon="🕰️", layout="wide")

# ---------------- CSS ----------------
st.markdown(
    """
    <style>
        /* Hide Streamlit sidebar collapse/expand control (safe selector) */
        [data-testid="collapsedControl"] {
            display: none !important;
            visibility: hidden !important;
        }

        * { font-family: 'Segoe UI', sans-serif !important; }
        h1 { color: #1E88E5; font-weight: 700; }
        h2, h3, h4 { color: #1565C0; font-weight: 600; }
        .stButton>button {
            background-color: #1E88E5;
            color: white;
            border-radius: 10px;
            font-weight: 600;
            transition: 0.2s;
        }
        .stButton>button:hover { background-color: #1565C0; }
        .metric-card {
            background: #F5F9FF;
            padding: 12px 16px;
            border-radius: 10px;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 10px;
        }
        .block-container { max-width: 1100px; margin: auto; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- HEADER ----------------
st.title("🕰️ TimeShiftAI — Future Decision Lab")
st.markdown(
    """
### 🌍 Simulate, Compare, and Visualize Your Possible Tomorrows  
Discover how your **career choices**, **risk tolerance**, and **financial lifestyle** influence your future wealth and happiness.
"""
)

# ---------------- INPUT SECTION (single page) ----------------
col1, col2, col3 = st.columns(3)
with col1:
    currency = st.selectbox("Preferred Currency 💱", ["AED", "USD", "INR", "EUR", "GBP"])
    salary = st.number_input(f"Monthly Salary ({currency})", value=15000, step=500)
    savings = st.number_input(f"Current Savings ({currency})", value=10000, step=1000)
with col2:
    family_expense = st.number_input(f"Monthly Family Expense ({currency})", value=5000, step=500)
    emi = st.number_input(f"Monthly EMIs ({currency})", value=2000, step=500)
    years = st.slider("Years to Simulate", 1, 20, 10)
with col3:
    risk_tolerance = st.slider("Risk Appetite (0 = Low, 10 = High)", 0, 10, 5)
    growth_bias = st.slider("Market Growth Bias (%)", 0, 15, 5)

# ---------------- CURRENCY CONVERSION ----------------
base_currency = "AED"
conversion_rate = 1.0
if currency != base_currency:
    try:
        response = requests.get(f"https://api.exchangerate.host/latest?base={base_currency}&symbols={currency}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # safe lookup
            conversion_rate = data.get("rates", {}).get(currency, 1.0)
        else:
            st.warning("⚠️ Currency conversion API unavailable. Showing AED values.")
    except Exception:
        st.warning("⚠️ Could not fetch currency rates. Using AED values.")
        conversion_rate = 1.0

# ---------------- SCENARIO DEFINITIONS ----------------
base_scenarios = {
    "Stay in Job": {"growth": 0.05 + growth_bias / 100, "volatility": 0.02},
    "Join Startup": {"growth": 0.12 + growth_bias / 100, "volatility": 0.08},
    "Go Freelance": {"growth": 0.08 + growth_bias / 100, "volatility": 0.05},
}

# ---------------- QUICK SCENARIO PROMPTS ----------------
st.subheader("⚙️ Quick Scenario Prompts")
sc1, sc2, sc3, sc4 = st.columns(4)

# scenario_mod accumulates a small additive change to growth rate
scenario_mod = 0.0
# copy inputs to local_mod variables so pressing a button updates for this run only
_salary = salary
_family_expense = family_expense
_savings = savings
_growth_bias = growth_bias

if sc1.button("📉 Economic Downturn"):
    _growth_bias = max(0, growth_bias - 5)
    scenario_mod = -0.03
elif sc2.button("💰 Salary Hike"):
    _salary = salary * 1.2
    scenario_mod = 0.02
elif sc3.button("🌍 Move Abroad"):
    _family_expense = family_expense * 1.3
    _salary = salary * 1.4
elif sc4.button("🚀 Start Side Hustle"):
    _savings = savings + 5000
    scenario_mod = 0.04

# apply scenario_mod to scenarios (create new dict so base remains unchanged)
scenarios = {
    name: {"growth": vals["growth"] + scenario_mod, "volatility": vals["volatility"]}
    for name, vals in base_scenarios.items()
}

# ---------------- SIMULATION ----------------
data_frames = []
for scenario_name, vals in scenarios.items():
    incomes = [_salary * 12]
    wealth = [_savings]
    for year in range(1, years + 1):
        # sample income change using normal noise
        income = incomes[-1] * (1 + np.random.normal(vals["growth"], vals["volatility"]))
        yearly_expense = (_family_expense + emi) * 12
        net = wealth[-1] + income - yearly_expense
        incomes.append(income)
        wealth.append(net)
    df = pd.DataFrame({"Year": range(0, years + 1), "Wealth": wealth})
    df["Scenario"] = scenario_name
    data_frames.append(df)

df_all = pd.concat(data_frames, ignore_index=True)
converted_df = df_all.copy()
converted_df["Wealth"] = converted_df["Wealth"] * conversion_rate

# ---------------- RESULTS VISUALIZATION ----------------
st.markdown("---")
colL, colR = st.columns([1.7, 1])

with colL:
    st.subheader(f"📈 Projected Wealth Over {years} Years ({currency})")
    pivot = converted_df.pivot(index="Year", columns="Scenario", values="Wealth")
    st.line_chart(pivot, height=420)

with colR:
    st.subheader("📊 Snapshot Insights")
    last_values = df_all[df_all["Year"] == years][["Scenario", "Wealth"]].reset_index(drop=True)
    best_row = last_values.loc[last_values["Wealth"].idxmax()]
    worst_row = last_values.loc[last_values["Wealth"].idxmin()]
    best_wealth = float(best_row["Wealth"]) * conversion_rate
    worst_wealth = float(worst_row["Wealth"]) * conversion_rate
    st.metric("💹 Best Path", best_row["Scenario"], f"{best_wealth:,.0f} {currency}")
    st.metric("⚠️ Lowest Path", worst_row["Scenario"], f"{worst_wealth:,.0f} {currency}")

    # simple happiness mock
    happiness = {
        "Stay in Job": np.random.uniform(6, 8),
        "Go Freelance": np.random.uniform(7, 9),
        "Join Startup": np.random.uniform(4, 7),
    }
    h_df = pd.DataFrame.from_dict(happiness, orient="index", columns=["Happiness Score"])
    st.bar_chart(h_df)

# ---------------- SESSION MEMORY ----------------
if "memory" not in st.session_state:
    st.session_state.memory = deque(maxlen=3)

# ---------------- AI ADVISOR ----------------
st.markdown("---")
st.subheader("🤖 TimeShiftAI Advisor")

user_prompt = st.text_input("Ask TimeShiftAI (e.g., 'Should I join a startup or keep my job?')")

def get_ai_response(prompt: str, memory, risk_tol: int):
    history = " | ".join(list(memory))
    if risk_tol <= 3:
        context_tip = "You prefer safety — prioritize stable income and an emergency fund."
    elif risk_tol <= 7:
        context_tip = "You have a balanced appetite — diversify and keep optional experiments small."
    else:
        context_tip = "You can accept volatility — consider higher-growth opportunities with risk management."

    p = prompt.lower()
    if "startup" in p:
        return f"Startups can offer higher returns but are volatile. {context_tip}"
    if "freelance" in p:
        return f"Freelancing gives flexibility; ensure steady clients and 6+ months runway. {context_tip}"
    if "job" in p:
        return f"Staying gives stability; negotiate raises and upskilling to grow safely. {context_tip}"
    if "save" in p or "savings" in p:
        return f"Aim for automated savings of 20–30% where possible. Consider liquid instruments for your emergency fund. {context_tip}"
    if "investment" in p or "invest" in p:
        return f"Consider a diversified mix (e.g., equity + fixed income). Match risk to your time horizon. {context_tip}"
    # default response referencing memory
    if history:
        return f"Based on your recent questions ({history}), keep a flexible plan and simulate 'what-if' scenarios. {context_tip}"
    return f"I suggest you try small controlled experiments (e.g., 6-month freelancing trial). {context_tip}"

if user_prompt:
    # save prompt
    st.session_state.memory.append(user_prompt)
    answer = get_ai_response(user_prompt, st.session_state.memory, risk_tolerance)
    st.success(answer)

st.caption("🧠 Tip: TimeShiftAI remembers your last 3 prompts to give better contextual answers.")
