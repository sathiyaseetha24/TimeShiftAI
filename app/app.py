# app/app.py
import streamlit as st
import pandas as pd
import numpy as np
import requests
from collections import deque

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="TimeShiftAI — Future Decision Lab", page_icon="🕰️", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
    <style>
        * { font-family: 'Segoe UI', sans-serif !important; }
        h1 { color: #1E88E5; font-weight: 700; }
        h2, h3, h4 { color: #1565C0; font-weight: 600; }
        .stButton>button {
            background-color: #1E88E5;
            color: white;
            border-radius: 10px;
            font-weight: 600;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #1565C0;
        }
        .stTextInput>div>div>input {
            border-radius: 10px;
            border: 1px solid #1E88E5;
        }
        .metric-card {
            background: #F5F9FF;
            padding: 12px 16px;
            border-radius: 10px;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🕰️ TimeShiftAI — Future Decision Lab")
st.markdown("""
### 🌍 Simulate, Compare, and Visualize Your Possible Tomorrows  
Discover how your **career choices**, **risk tolerance**, and **financial lifestyle** influence your future wealth and happiness.
""")

# ---------------- INPUT SECTION ----------------
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
        response = requests.get(f"https://api.exchangerate.host/latest?base={base_currency}&symbols={currency}")
        if response.status_code == 200:
            data = response.json()
            conversion_rate = data["rates"][currency]
    except:
        st.warning("⚠️ Currency conversion API unavailable. Using AED values.")

# ---------------- SCENARIO DEFINITIONS ----------------
base_scenarios = {
    "Stay in Job": {"growth": 0.05 + growth_bias / 100, "volatility": 0.02},
    "Join Startup": {"growth": 0.12 + growth_bias / 100, "volatility": 0.08},
    "Go Freelance": {"growth": 0.08 + growth_bias / 100, "volatility": 0.05},
}

# ---------------- SCENARIO BUTTONS ----------------
st.subheader("⚙️ Quick Scenario Prompts")
sc1, sc2, sc3, sc4 = st.columns(4)

scenario_mod = 0
if sc1.button("📉 Economic Downturn"):
    growth_bias -= 5
    scenario_mod = -0.03
elif sc2.button("💰 Salary Hike"):
    salary *= 1.2
    scenario_mod = 0.02
elif sc3.button("🌍 Move Abroad"):
    family_expense *= 1.3
    salary *= 1.4
elif sc4.button("🚀 Start Side Hustle"):
    savings += 5000
    scenario_mod = 0.04

# Update growth with scenario_mod
for s in base_scenarios:
    base_scenarios[s]["growth"] += scenario_mod

# ---------------- SIMULATION ----------------
data = []
for scenario, vals in base_scenarios.items():
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
converted_df = df_all.copy()
converted_df["Wealth"] = converted_df["Wealth"] * conversion_rate

# ---------------- RESULTS ----------------
colL, colR = st.columns([1.7, 1])
with colL:
    st.subheader(f"📈 Projected Wealth Over {years} Years ({currency})")
    st.line_chart(converted_df.pivot(index="Year", columns="Scenario", values="Wealth"), height=420)

with colR:
    st.subheader("📊 Insights")
    last_values = df_all[df_all["Year"] == years][["Scenario", "Wealth"]]
    best_row = last_values.loc[last_values["Wealth"].idxmax()]
    worst_row = last_values.loc[last_values["Wealth"].idxmin()]
    best_wealth = float(best_row["Wealth"]) * conversion_rate
    worst_wealth = float(worst_row["Wealth"]) * conversion_rate
    st.metric("💹 Best Path", best_row["Scenario"], f"{best_wealth:,.0f} {currency}")
    st.metric("⚠️ Lowest Path", worst_row["Scenario"], f"{worst_wealth:,.0f} {currency}")

# ---------------- MEMORY SYSTEM ----------------
if "memory" not in st.session_state:
    st.session_state.memory = deque(maxlen=3)

# ---------------- AI ADVISOR ----------------
st.markdown("---")
st.subheader("🤖 TimeShiftAI Advisor")

user_prompt = st.text_input("Ask TimeShiftAI (e.g., 'Should I join a startup or keep my job?')")

def get_ai_response(prompt, memory, risk_tolerance):
    history = " | ".join(memory)
    context_tip = ""
    if risk_tolerance <= 3:
        context_tip = "Since your risk tolerance is low, prioritize safety and consistent returns."
    elif risk_tolerance <= 7:
        context_tip = "With moderate risk tolerance, consider hybrid or diversified strategies."
    else:
        context_tip = "Your high risk tolerance allows for bold moves with potential volatility."

    if "startup" in prompt.lower():
        return f"Joining a startup can yield higher long-term returns but requires patience. {context_tip}"
    elif "freelance" in prompt.lower():
        return f"Freelancing offers flexibility and autonomy. {context_tip}"
    elif "job" in prompt.lower():
        return f"Staying in your current job ensures stability. {context_tip}"
    elif "save" in prompt.lower():
        return f"Aim to save 25–30% of income. Use SIPs or index funds. {context_tip}"
    elif "investment" in prompt.lower():
        return f"Diversify your portfolio: 60% equity, 40% fixed assets. {context_tip}"
    else:
        return f"Based on recent topics ({history}), maintain a flexible plan that balances wealth and peace of mind. {context_tip}"

if user_prompt:
    st.session_state.memory.append(user_prompt)
    response = get_ai_response(user_prompt, st.session_state.memory, risk_tolerance)
    st.success(response)

# ---------------- FOOTER ----------------
st.caption("🧠 Tip: Ask consecutive questions — TimeShiftAI remembers your last 3 for better context.")
