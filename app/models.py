from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PortfolioPosition(BaseModel):
    symbol: str = Field(..., description="Ticker symbol, e.g. AAPL")
    shares: float = Field(..., gt=0)
    avg_cost: float = Field(..., gt=0)


class RiskProfile(BaseModel):
    horizon_years: int = Field(10, ge=1, le=50)
    max_drawdown_tolerance: float = Field(0.2, ge=0.01, le=0.8)
    prefers_income: bool = False
    esg_focus: bool = False


class UserContext(BaseModel):
    user_id: str
    portfolio: List[PortfolioPosition] = Field(default_factory=list)
    risk_profile: RiskProfile = Field(default_factory=RiskProfile)


class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[UserContext] = None


class ToolResult(BaseModel):
    tool_name: str
    summary: str
    payload: Dict


class ChatResponse(BaseModel):
    answer: str
    steps: List[ToolResult]
    memory_hits: List[str]
