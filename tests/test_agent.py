from __future__ import annotations

import pandas as pd

from app.agent import WealthManagementAgent
from app.models import PortfolioPosition, RiskProfile, UserContext


def fake_download(tickers, period, interval, auto_adjust, progress):
    if period == "5d":
        idx = pd.date_range("2024-01-01", periods=5)
        if len(tickers) == 1:
            return pd.DataFrame({"Close": [100, 101, 102, 103, 104]}, index=idx)
        cols = pd.MultiIndex.from_product([["Close"], tickers])
        data = [[100 + i + j for j in range(len(tickers))] for i in range(5)]
        return pd.DataFrame(data, index=idx, columns=cols)

    idx = pd.date_range("2024-01-01", periods=260)
    if len(tickers) == 1:
        return pd.DataFrame({"Close": [100 + i * 0.1 for i in range(260)]}, index=idx)
    cols = pd.MultiIndex.from_product([["Close"], tickers])
    data = [[100 + i * 0.1 + j for j in range(len(tickers))] for i in range(260)]
    return pd.DataFrame(data, index=idx, columns=cols)


def test_agent_flow(monkeypatch):
    monkeypatch.setattr("app.tools.yf.download", fake_download)

    agent = WealthManagementAgent()
    ctx = UserContext(
        user_id="u1",
        portfolio=[PortfolioPosition(symbol="AAPL", shares=10, avg_cost=90)],
        risk_profile=RiskProfile(),
    )

    out = agent.run("u1", "Analyze risk and propose strategy", ctx)
    assert len(out.steps) >= 2
    assert any(step.tool_name == "assess_portfolio_risk" for step in out.steps)
