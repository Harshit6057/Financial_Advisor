from __future__ import annotations

import json

import requests
import streamlit as st

st.set_page_config(page_title="Wealth Management Agent", layout="wide")
st.title("💼 Wealth Management Agentic AI (Free Stack)")
st.caption("FastAPI + ChromaDB + yfinance + Streamlit")

api_url = st.sidebar.text_input("Backend URL", value="http://localhost:8000/chat")
user_id = st.sidebar.text_input("User ID", value="demo-user")

portfolio_json = st.text_area(
    "Portfolio JSON",
    value='[{"symbol":"AAPL","shares":20,"avg_cost":160},{"symbol":"MSFT","shares":10,"avg_cost":300},{"symbol":"VOO","shares":15,"avg_cost":380}]',
    height=120,
)

risk_json = st.text_area(
    "Risk Profile JSON",
    value='{"horizon_years":10,"max_drawdown_tolerance":0.2,"prefers_income":false,"esg_focus":false}',
    height=100,
)

message = st.text_input("Ask your assistant", value="Analyze my portfolio risk and propose an allocation strategy.")

if st.button("Run Agent"):
    payload = {
        "user_id": user_id,
        "message": message,
        "context": {
            "user_id": user_id,
            "portfolio": json.loads(portfolio_json),
            "risk_profile": json.loads(risk_json),
        },
    }
    try:
        resp = requests.post(api_url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        st.subheader("Assistant Response")
        st.markdown(data["answer"])
        st.subheader("Executed Tool Steps")
        st.json(data["steps"])
        st.subheader("Memory Hits")
        st.json(data["memory_hits"])
    except Exception as exc:
        st.error(f"Request failed: {exc}")
