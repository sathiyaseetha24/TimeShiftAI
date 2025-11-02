import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="TimeShiftAI", layout="wide")

st.title("🕰️ TimeShiftAI — Alternate Futures for Your Career")
st.markdown("### *Simulate, Compare, and See Your Possible Tomorrows*")

st.sidebar.header("🎯 Your Current Situation")

currency = st.sidebar.selectbox("Currency", ["AED", "USD", "INR", "EUR", "GBP"])
salary = st.sidebar.number_input(f"Current Salary ({currency})", value=15000)
family_expense = st.sidebar.number_input(f"Monthly Family Expense ({currency})", value=5000)
emi = st.sidebar.number_input(f"Total EMIs ({currency})", value=2000)
savings = st.sidebar.number_input(f"Current Savings ({currency})", value=10000)
risk_tolerance = st.sidebar.slider("Risk Appetite", 0, 10, 5)

years = st.sidebar.slider("Years to Simulate", 1, 20, 10)
scenario = st.sidebar.selectbox("Choose Path", ["Stay in Job", "Join Startup", "Go Freelance"])

# Basic simulation logic
growth = {
    "Stay in Job": 0.08,
    "Join Startup": 0.15,
    "Go Freelance": 0.12
}[scenario]

future_income = [salary * ((1 + growth) ** i) for i in range(years + 1)]
net_savings = [savings + (income - family_expense*12 - emi*12) for income in future_income]

st.subheader(f"📊 Projected Wealth for '{scenario}' ({currency})")
st.line_chart(pd.DataFrame(net_savings, columns=["Predicted Wealth"]))

st.markdown("### 💡 Insight:")
if risk_tolerance < 4 and scenario == "Join Startup":
    st.warning("High risk! Startup path may not align with your risk tolerance.")
elif risk_tolerance > 7 and scenario == "Stay in Job":
    st.info("You may be under-challenged. Explore higher growth paths like startups or freelancing.")
else:
    st.success("Your choice aligns well with your financial and personal profile!")
