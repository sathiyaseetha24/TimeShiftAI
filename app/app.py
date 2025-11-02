# app/app.py
import requests
import streamlit as st
import pandas as pd
import numpy as np
from collections import deque

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TimeShiftAI — Future Decision Lab",
    page_icon="🕰️",
    layout="wide",
)

# ---------------- SAFE CSS ----------------
st.markdown(
    """
    <style>
        /* Hide Streamlit sidebar controls safely */
        [data-testid="collapsedControl"], [data-testid="stSidebar"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Basic UI polish */
        * { font-family: 'Segoe UI', sans-serif !important; }
        h1 { color: #1E88E5; font-weight: 700; }
        h2, h3, h4 { color: #1565C0; font-weight: 600; }

        .input-panel {
            background: #F8FBFF;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 18px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }

        .metric-card {
            background: #F5F9FF;
            padding: 12px;
            border-radius: 10px;
        }

        .block-container { max-width: 1150px; margin: auto; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- HEADER ----------------
st.title("🕰️ TimeShiftAI — Future Decision Lab")
st.markdown(
    "### 🌍 Simulate, Compare, and Visualize Your Possible Tomorrows\n"
    "Understand how career choices, risk tolerance, and financial commitments shape your future wealth."
)

# ---------------- USER INPUT SECTION ----------------
st.markdown("#### ⚙️ Configure Your Profile and Simulation")

# Row 1: Core Finances
col1, col2, col3 = st.columns(3)
with col1:
    currency = st.selectbox("Preferred Currency 💱", ["AED", "USD", "INR", "EUR", "GBP"])
    salary = st.number_input(f"Monthly Salary ({currency})", value=15000, step=500)
with col2:
    family_expense = st.number_input(f"Monthly Family Expense ({currency})", value=5000, step=250)
    emi = st.number_input(f"Monthly EMIs ({currency})", value=2000, step=250)
with col3:
    savings = st.number_input(f"Current Savings ({currency})", value=10000, step=500)

# Small visual divider
st.markdown("<hr style='margin: 1.5rem 0; border: 1px solid #eee;'>", unsafe_allow_html=True)
st.markdown("#### 🎯 Simulation Settings")

# Row 2: Simulation Parameters
col4, col5, col6 = st.columns(3)
with col4:
    risk_tolerance = st.slider("Risk Appetite (0 = Low, 10 = High)", 0, 10, 5)
with col5:
    years = st.slider("Years to Simulate", 1, 20, 10)
with col6:
    growth_bias = st.slider("Market Growth Bias (%)", 0, 15, 5)



# ---------------- Currency conversion (safe) ----------------
base_currency = "AED"
conversion_rate = 1.0
if currency != base_currency:
    try:
        resp = requests.get(f"https://api.exchangerate.host/latest?base={base_currency}&symbols={currency}", timeout=5)
        if resp.status_code == 200:
            rates = resp.json().get("rates", {})
            conversion_rate = float(rates.get(currency, 1.0))
        else:
            st.warning("⚠️ Currency API returned an error. Values shown in AED.")
            conversion_rate = 1.0
    except Exception:
        st.warning("⚠️ Could not fetch currency rates. Values shown in AED.")
        conversion_rate = 1.0

# ---------------- Scenario definitions ----------------
scenarios = {
    "Stay in Job": {"growth": 0.05 + growth_bias / 100, "volatility": 0.02},
    "Join Startup": {"growth": 0.12 + growth_bias / 100, "volatility": 0.08},
    "Go Freelance": {"growth": 0.08 + growth_bias / 100, "volatility": 0.05},
}

# ---------------- Simulation ----------------
data = []
for scenario_name, params in scenarios.items():
    incomes = [salary * 12]
    wealth = [savings]
    for year in range(1, years + 1):
        # income evolves by growth + stochastic noise (normal)
        inc = incomes[-1] * (1 + np.random.normal(params["growth"], params["volatility"]))
        yearly_expense = (family_expense + emi) * 12
        net = wealth[-1] + inc - yearly_expense
        incomes.append(inc)
        wealth.append(net)
    df = pd.DataFrame({"Year": list(range(0, years + 1)), "Wealth": wealth})
    df["Scenario"] = scenario_name
    data.append(df)

df_all = pd.concat(data, ignore_index=True)
df_display = df_all.copy()
df_display["Wealth"] = df_display["Wealth"] * conversion_rate

# ---------------- Results area ----------------
st.markdown("---")
st.markdown("### 📈 Simulation Results")

left_col, right_col = st.columns([1.7, 1])
with left_col:
    st.subheader(f"Projected Wealth Over {years} Years ({currency})")
    pivot = df_display.pivot(index="Year", columns="Scenario", values="Wealth")
    st.line_chart(pivot, height=420)

with right_col:
    st.subheader("Snapshot Insights")
    last_values = df_all[df_all["Year"] == years][["Scenario", "Wealth"]].reset_index(drop=True)
    # protect against degenerate cases
    if not last_values.empty:
        best_row = last_values.loc[last_values["Wealth"].idxmax()]
        worst_row = last_values.loc[last_values["Wealth"].idxmin()]
        best_wealth = float(best_row["Wealth"]) * conversion_rate
        worst_wealth = float(worst_row["Wealth"]) * conversion_rate
        st.metric("💹 Best Financial Path", best_row["Scenario"], f"{best_wealth:,.0f} {currency}")
        st.metric("⚠️ Lowest Return Path", worst_row["Scenario"], f"{worst_wealth:,.0f} {currency}")
    else:
        st.write("No results to display.")

    # Simple happiness mock (illustrative)
    happiness = {
        "Stay in Job": np.random.uniform(6, 8),
        "Go Freelance": np.random.uniform(7, 9),
        "Join Startup": np.random.uniform(4, 7),
    }
    hdf = pd.DataFrame.from_dict(happiness, orient="index", columns=["Happiness Score"])
    st.bar_chart(hdf)

# ---------------- Decision summary ----------------
st.markdown("---")
st.subheader("💡 Decision Intelligence Summary")
if risk_tolerance <= 3:
    st.info("Your profile shows low risk tolerance. A stable job with controlled savings and modest investments is recommended.")
elif 4 <= risk_tolerance <= 7:
    st.info("Medium risk tolerance: consider hybrid strategies (part-time freelancing / side projects + core job) and diversified investment.")
else:
    st.success("High risk tolerance: you may consider higher-growth paths (startup, freelancing) while maintaining a clear contingency fund.")

st.caption("Tip: adjust EMIs, family expense and growth bias to see the metric shifts in real time.")

# ---------------- Session-only AI chat memory ----------------
if "chat_memory" not in st.session_state:
    # remember up to 5 last prompts during the session
    st.session_state.chat_memory = deque(maxlen=5)

st.markdown("---")
st.subheader("🤖 TimeShiftAI Advisor — Professional, Analytical")

prompt = st.text_input("Ask TimeShiftAI a question (e.g., 'Should I join a startup or stay in my job?')")

def compose_context(memory_deque, salary, savings, emi, family_expense, risk_tol, years):
    """Create a short analytical context summary for the AI response."""
    mem_summary = " ; ".join(list(memory_deque)) if memory_deque else "no recent questions"
    context = (
        f"Context: salary={salary}, savings={savings}, emi={emi}, family_expense={family_expense}, "
        f"risk_tolerance={risk_tol}, years={years}. Recent prompts: {mem_summary}."
    )
    return context

def analytical_response(user_q: str, memory_deque, salary, savings, emi, family_expense, risk_tol, years):
    """Return a professional analytical response derived from user question + session memory + numeric inputs."""
    ctx = compose_context(memory_deque, salary, savings, emi, family_expense, risk_tol, years)

    q = user_q.lower()
    # Basic rule-based analysis. This is deterministic and data-aware (no external LLM).
    if "startup" in q:
        # give data-aware guidance
        est_runway = savings / ((family_expense + emi) if (family_expense + emi) > 0 else 1)
        advice = (
            f"Joining a startup typically increases income volatility. With current savings of {savings:,.0f} "
            f"and monthly outflows {(family_expense + emi):,.0f}, your runway is ~{est_runway:.1f} months. "
            "If runway < 6 months, secure additional buffer or phased transition. "
        )
        if risk_tol <= 3:
            advice += "Your low risk tolerance suggests avoiding full-time startup exposure."
        elif risk_tol <= 7:
            advice += "Consider a part-time pilot or equity-for-lower-pay arrangement initially."
        else:
            advice += "Your profile supports higher risk; ensure legal/financial protections and plan exits."
        return f"{advice}\n\n{ctx}"
    if "freelance" in q or "freelancing" in q:
        avg_monthly_need = (family_expense + emi)
        advice = (
            f"Freelancing gives flexibility but variable revenue. Target building a 3–6 month revenue pipeline before leaving a steady job. "
            f"With monthly obligations of {avg_monthly_need:,.0f}, ensure contracts or retained clients cover core expenses."
        )
        if risk_tol <= 3:
            advice += " Given low risk tolerance, keep freelancing as a secondary income initially."
        else:
            advice += " Consider a 3–6 month trial period and track client churn metrics."
        return f"{advice}\n\n{ctx}"
    if "save" in q or "savings" in q or "save more" in q:
        monthly_income = salary
        recommended_pct = 0.25 if risk_tol >= 4 else 0.2
        recommendation = (
            f"Analytical recommendation: target saving {int(recommended_pct*100)}% of monthly income. "
            f"Automate transfers to a liquid emergency fund first, then systematic investments (monthly)."
        )
        return f"{recommendation}\n\n{ctx}"
    if "compare" in q and "job" in q and "startup" in q:
        # quick quantitative comparison using first-year expectation
        job_growth = scenarios["Stay in Job"]["growth"]
        startup_growth = scenarios["Join Startup"]["growth"]
        compare = (
            f"Model comparison (first-order): expected growth rate job={job_growth:.2%}, startup={startup_growth:.2%}. "
            "Startups show higher mean growth but higher volatility; quantify required emergency buffer and expected income variance."
        )
        return f"{compare}\n\n{ctx}"
    # fallback professional answer referencing memory and inputs
    fallback = (
        "I recommend running 'what-if' experiments in the simulator for scenarios you care about (e.g., +20% salary, +30% family expenses). "
        "If you provide a specific hypothesis (e.g., 'What if my salary increases by 20% in 2 years?') I will produce a focused analytical recommendation."
    )
    return f"{fallback}\n\n{ctx}"

# When user submits a prompt:
if prompt:
    # record prompt in session memory
    st.session_state.chat_memory.append(prompt)
    # compute response
    resp_text = analytical_response(
        prompt,
        st.session_state.chat_memory,
        salary,
        savings,
        emi,
        family_expense,
        risk_tolerance,
        years,
    )
    # show professional tone response
    st.markdown("**TimeShiftAI (Analytical Advisor):**")
    st.write(resp_text)

# show recent memory (session)
if st.session_state.chat_memory:
    st.markdown("**Recent prompts this session:**")
    for idx, p in enumerate(reversed(st.session_state.chat_memory), 1):
        st.write(f"{idx}. {p}")

st.caption("Session memory: TimeShiftAI remembers the last 5 prompts for context while the tab is open.")
