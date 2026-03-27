# Wealth Management Agentic AI Chatbot (Free Alternative to MS Fabric)

This project is a **fully working, local-first Agentic AI financial assistant** that replaces paid Fabric components with free/open-source tools.

## What it does

- Ingests user portfolio + risk profile.
- Autonomously selects and executes specialized tools based on user intent:
  - Stock/position analysis
  - Portfolio risk assessment (volatility, VaR, CVaR)
  - Investment strategy generation
  - Risk mitigation plan
- Stores long-term conversation memory in **ChromaDB vector store**.
- Exposes a **FastAPI** chat API.
- Includes a **Streamlit UI** for interactive use.

## Free stack used

- **FastAPI** (backend API)
- **Streamlit** (chat/dashboard UI)
- **yfinance** (market data)
- **ChromaDB** (vector memory)
- **Pandas/Numpy** (risk analytics)

> No Microsoft Fabric required.

---

## Architecture

```text
User -> Streamlit UI -> FastAPI /chat -> WealthManagementAgent
                                         |- Tool: analyze_positions
                                         |- Tool: assess_portfolio_risk
                                         |- Tool: generate_investment_strategy
                                         |- Tool: risk_mitigation_plan
                                         \- ChromaDB memory (retrieve + store)
```

The agent follows an **intent-driven planning** approach:
1. Parse query intent.
2. Pick relevant tools dynamically.
3. Execute multi-step workflow.
4. Build response from tool outputs.
5. Persist conversation for future personalization.

---

## Project structure

```text
.
├── app
│   ├── agent.py
│   ├── main.py
│   ├── memory.py
│   ├── models.py
│   ├── tools.py
│   └── data/sample_portfolio.json
├── streamlit_app.py
├── tests/test_agent.py
└── requirements.txt
```

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run backend API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

## Run UI

```bash
streamlit run streamlit_app.py --server.port 8501
```

Open `http://localhost:8501`.

---

## API usage example

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo-user",
    "message": "Analyze my portfolio risk and propose strategy",
    "context": {
      "user_id": "demo-user",
      "portfolio": [
        {"symbol": "AAPL", "shares": 20, "avg_cost": 160},
        {"symbol": "MSFT", "shares": 10, "avg_cost": 300},
        {"symbol": "VOO", "shares": 15, "avg_cost": 380}
      ],
      "risk_profile": {
        "horizon_years": 10,
        "max_drawdown_tolerance": 0.2,
        "prefers_income": false,
        "esg_focus": false
      }
    }
  }'
```

---

## Notes

- Market data depends on Yahoo Finance availability.
- First ChromaDB run may initialize local vector storage in `.chroma/`.
- This is designed as a modular baseline; you can add more tools (tax optimization, Monte Carlo forecasting, factor attribution, etc.).

## Testing

```bash
pytest -q
```
