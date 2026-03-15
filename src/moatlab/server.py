"""MoatLab Web API — FastAPI REST interface for value investing system."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from moatlab.store.database import init_db
from moatlab.tools.portfolio import (
    add_position,
    sell_position,
    get_portfolio,
    get_transaction_history,
    get_portfolio_performance,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MoatLab API",
    description="巴菲特/段永平价值投资系统 REST API",
    version="0.3.0",
)


@app.on_event("startup")
def startup():
    init_db()


# ── Request/Response Models ─────────────────────────────────────────

class TradeRequest(BaseModel):
    ticker: str
    shares: float
    price: float
    trade_date: str | None = None
    notes: str = ""


class AnalyzeRequest(BaseModel):
    mode: str = "full"  # full, financial, valuation, moat, management


class ScreenRequest(BaseModel):
    roe_min: float | None = None
    debt_to_equity_max: float | None = None
    gross_margin_min: float | None = None
    pe_max: float | None = None
    sector: str | None = None


# ── Health ──────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "moatlab"}


# ── Portfolio endpoints ─────────────────────────────────────────────

@app.get("/api/portfolio")
def api_get_portfolio():
    """Get all positions with real-time market values."""
    return get_portfolio()


@app.post("/api/portfolio/buy")
def api_buy(req: TradeRequest):
    """Record a stock purchase."""
    req.ticker = req.ticker.upper()
    trade_date = req.trade_date or date.today().isoformat()
    return add_position(req.ticker, req.shares, req.price, trade_date, req.notes)


@app.post("/api/portfolio/sell")
def api_sell(req: TradeRequest):
    """Record a stock sale."""
    req.ticker = req.ticker.upper()
    trade_date = req.trade_date or date.today().isoformat()
    result = sell_position(req.ticker, req.shares, req.price, trade_date, req.notes)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.get("/api/portfolio/performance")
def api_performance():
    """Get portfolio performance summary."""
    return get_portfolio_performance()


@app.get("/api/portfolio/history")
def api_history(ticker: str | None = None, limit: int = 50):
    """Get transaction history."""
    return get_transaction_history(ticker, limit)


@app.post("/api/portfolio/review")
def api_portfolio_review():
    """AI-driven portfolio review — check if investment thesis still holds."""
    from moatlab.agents.portfolio import PortfolioAgent
    agent = PortfolioAgent()
    result = agent.manage(
        "请回顾我当前的持仓组合，检查每个持仓的投资逻辑是否仍然成立，给出整体评估和建议。"
    )
    return {"result": result}


# ── Analysis endpoints ──────────────────────────────────────────────

@app.post("/api/analyze/{ticker}")
def api_analyze(ticker: str, req: AnalyzeRequest | None = None):
    """Run value investing analysis on a stock."""
    ticker = ticker.upper()
    mode = req.mode if req else "full"

    if mode == "full":
        from moatlab.agents.orchestrator import Orchestrator
        orchestrator = Orchestrator()
        return orchestrator.analyze(ticker)
    elif mode == "financial":
        from moatlab.agents.financial import FinancialAgent
        return {"result": FinancialAgent().analyze(ticker)}
    elif mode == "valuation":
        from moatlab.agents.valuation import ValuationAgent
        return {"result": ValuationAgent().analyze(ticker)}
    elif mode == "moat":
        from moatlab.agents.moat import MoatAgent
        return {"result": MoatAgent().analyze(ticker)}
    elif mode == "management":
        from moatlab.agents.management import ManagementAgent
        return {"result": ManagementAgent().analyze(ticker)}
    else:
        raise HTTPException(status_code=400, detail=f"未知分析模式: {mode}")


@app.post("/api/screen")
def api_screen(req: ScreenRequest | None = None):
    """Screen stocks based on value investing criteria."""
    parts = []
    if req:
        if req.roe_min is not None:
            parts.append(f"ROE ≥ {req.roe_min*100:.0f}%")
        if req.debt_to_equity_max is not None:
            parts.append(f"负债率 ≤ {req.debt_to_equity_max}")
        if req.gross_margin_min is not None:
            parts.append(f"毛利率 ≥ {req.gross_margin_min*100:.0f}%")
        if req.pe_max is not None:
            parts.append(f"PE ≤ {req.pe_max}")
        if req.sector:
            parts.append(f"行业: {req.sector}")

    criteria = "、".join(parts) if parts else None

    from moatlab.agents.screener import ScreenerAgent
    agent = ScreenerAgent()
    return {"result": agent.screen(criteria)}


# ── Lark Bot webhook ──────────────────────────────────────────────

@app.post("/feishu/events")
async def lark_webhook(request: Request):
    """Lark 事件回调入口（HTTP Callback 模式）。"""
    body = await request.json()

    # URL Verification — Lark 配置 webhook 时的验证请求
    if body.get("type") == "url_verification":
        return {"challenge": body["challenge"]}

    # 消息事件处理
    from moatlab.channels.lark import handle_event
    return handle_event(body)
