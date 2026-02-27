from __future__ import annotations

from typing import List

from app.memory import ConversationMemory
from app.models import ChatResponse, ToolResult, UserContext
from app.tools import (
    analyze_positions,
    assess_portfolio_risk,
    generate_investment_strategy,
    risk_mitigation_plan,
)


class WealthManagementAgent:
    def __init__(self) -> None:
        self.memory = ConversationMemory()

    def _pick_tools(self, message: str) -> List[str]:
        msg = message.lower()
        selected = []
        if any(k in msg for k in ["position", "holding", "portfolio", "stock"]):
            selected.append("analyze_positions")
        if any(k in msg for k in ["risk", "drawdown", "var", "volatility"]):
            selected.append("assess_portfolio_risk")
        if any(k in msg for k in ["strategy", "invest", "allocation", "plan"]):
            selected.append("generate_investment_strategy")
        if any(k in msg for k in ["mitigate", "hedge", "protect", "reduce risk"]):
            selected.append("risk_mitigation_plan")

        if not selected:
            selected = [
                "analyze_positions",
                "assess_portfolio_risk",
                "generate_investment_strategy",
            ]
        return selected

    def run(self, user_id: str, message: str, context: UserContext | None) -> ChatResponse:
        ctx = context or UserContext(user_id=user_id)
        memory_hits = self.memory.query(user_id=user_id, query_text=message)

        selected = self._pick_tools(message)
        steps: List[ToolResult] = []
        risk_payload = {}

        if "analyze_positions" in selected:
            output = analyze_positions(ctx.portfolio)
            steps.append(ToolResult(tool_name="analyze_positions", summary=output.summary, payload=output.payload))

        if "assess_portfolio_risk" in selected:
            output = assess_portfolio_risk(ctx.portfolio)
            risk_payload = output.payload
            steps.append(ToolResult(tool_name="assess_portfolio_risk", summary=output.summary, payload=output.payload))

        if "generate_investment_strategy" in selected:
            output = generate_investment_strategy(risk_payload, ctx.risk_profile)
            steps.append(ToolResult(tool_name="generate_investment_strategy", summary=output.summary, payload=output.payload))

        if "risk_mitigation_plan" in selected:
            output = risk_mitigation_plan(risk_payload, ctx.risk_profile)
            steps.append(ToolResult(tool_name="risk_mitigation_plan", summary=output.summary, payload=output.payload))

        answer_parts = [f"- {s.tool_name}: {s.summary}" for s in steps]
        if memory_hits:
            answer_parts.append("- Used memory from prior sessions to personalize guidance.")
        answer = "\n".join(answer_parts)

        self.memory.add(user_id=user_id, role="user", text=message)
        self.memory.add(user_id=user_id, role="assistant", text=answer)

        return ChatResponse(answer=answer, steps=steps, memory_hits=memory_hits)
