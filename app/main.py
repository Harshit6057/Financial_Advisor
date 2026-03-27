from __future__ import annotations

from fastapi import FastAPI

from app.agent import WealthManagementAgent
from app.models import ChatRequest, ChatResponse

app = FastAPI(title="Wealth Management Agentic AI")
agent = WealthManagementAgent()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    return agent.run(user_id=req.user_id, message=req.message, context=req.context)
