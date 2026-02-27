from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd
import yfinance as yf

from app.models import PortfolioPosition, RiskProfile

TRADING_DAYS = 252


@dataclass
class ToolOutput:
    summary: str
    payload: Dict


def _portfolio_df(positions: List[PortfolioPosition]) -> pd.DataFrame:
    if not positions:
        return pd.DataFrame(columns=["symbol", "shares", "avg_cost"])
    return pd.DataFrame([p.model_dump() for p in positions])


def analyze_positions(positions: List[PortfolioPosition]) -> ToolOutput:
    df = _portfolio_df(positions)
    if df.empty:
        return ToolOutput("No positions provided.", {"positions": []})

    tickers = df["symbol"].tolist()
    latest = yf.download(tickers=tickers, period="5d", interval="1d", auto_adjust=True, progress=False)
    close = latest["Close"].iloc[-1] if isinstance(latest.columns, pd.MultiIndex) else latest["Close"]

    df["current_price"] = df["symbol"].map(close.to_dict())
    df["market_value"] = df["shares"] * df["current_price"]
    df["cost_basis"] = df["shares"] * df["avg_cost"]
    df["unrealized_pnl"] = df["market_value"] - df["cost_basis"]
    total = float(df["market_value"].sum())
    df["weight"] = df["market_value"] / total if total else 0.0

    top = df.sort_values("market_value", ascending=False).iloc[0]
    summary = (
        f"Portfolio market value is ${total:,.2f}. Largest position is {top['symbol']} "
        f"({top['weight']:.1%} weight)."
    )
    return ToolOutput(summary, {"positions": df.round(4).to_dict(orient="records"), "total_value": total})


def assess_portfolio_risk(positions: List[PortfolioPosition]) -> ToolOutput:
    df = _portfolio_df(positions)
    if df.empty:
        return ToolOutput("Cannot assess risk without portfolio positions.", {"volatility": None})

    tickers = df["symbol"].tolist()
    prices = yf.download(tickers=tickers, period="1y", interval="1d", auto_adjust=True, progress=False)["Close"]
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(name=tickers[0])

    rets = prices.pct_change().dropna()
    weights = np.array(df["shares"] * prices.iloc[-1].reindex(df["symbol"]).values)
    weights = weights / weights.sum()

    cov = rets.cov() * TRADING_DAYS
    port_vol = float(np.sqrt(weights.T @ cov.values @ weights))

    port_daily = rets.mul(weights, axis=1).sum(axis=1)
    var_95 = float(np.percentile(port_daily, 5))
    cvar_95 = float(port_daily[port_daily <= var_95].mean())

    risk_level = "Low" if port_vol < 0.15 else "Moderate" if port_vol < 0.25 else "High"
    summary = (
        f"Annualized volatility is {port_vol:.2%} ({risk_level} risk). "
        f"Daily VaR(95) is {var_95:.2%}, CVaR(95) is {cvar_95:.2%}."
    )
    return ToolOutput(
        summary,
        {"annualized_volatility": port_vol, "var_95": var_95, "cvar_95": cvar_95, "risk_level": risk_level},
    )


def generate_investment_strategy(risk: Dict, profile: RiskProfile) -> ToolOutput:
    risk_level = risk.get("risk_level", "Moderate")

    allocation = {"US Equity": 0.45, "International Equity": 0.2, "Bonds": 0.25, "Cash": 0.1}

    if risk_level == "High":
        allocation = {"US Equity": 0.35, "International Equity": 0.15, "Bonds": 0.35, "Cash": 0.15}
    elif risk_level == "Low" and profile.horizon_years >= 10:
        allocation = {"US Equity": 0.55, "International Equity": 0.25, "Bonds": 0.15, "Cash": 0.05}

    if profile.prefers_income:
        allocation["Bonds"] += 0.1
        allocation["US Equity"] -= 0.05
        allocation["International Equity"] -= 0.05

    if profile.esg_focus:
        note = "Prefer ESG-screened ETFs/funds in each allocation bucket."
    else:
        note = "Use low-cost index ETFs in each bucket."

    summary = f"Recommended strategic allocation prepared for a {risk_level.lower()}-risk portfolio."
    return ToolOutput(summary, {"allocation": allocation, "implementation_note": note})


def risk_mitigation_plan(risk: Dict, profile: RiskProfile) -> ToolOutput:
    actions = [
        "Rebalance quarterly if any asset class drifts by >5% from target.",
        "Keep 3-6 months of expenses in high-yield cash instruments.",
        "Use position limits: cap single-stock exposure at 10%.",
    ]

    if risk.get("annualized_volatility", 0) > profile.max_drawdown_tolerance:
        actions.append("Reduce equity exposure by 10% and shift to short-duration bonds.")
    if profile.horizon_years < 5:
        actions.append("Increase bond/cash exposure due to shorter investment horizon.")

    return ToolOutput("Risk mitigation actions generated.", {"actions": actions})
