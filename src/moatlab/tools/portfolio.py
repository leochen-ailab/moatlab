"""Portfolio management tools — CRUD operations + performance tracking."""

from __future__ import annotations

import logging
from datetime import date

import yfinance as yf

from moatlab.store.database import (
    init_db,
    add_transaction,
    get_positions,
    get_position,
    get_transactions,
)

logger = logging.getLogger(__name__)


def _ensure_db():
    """Ensure database tables exist."""
    init_db()


def add_position(
    ticker: str,
    shares: float,
    price: float,
    trade_date: str | None = None,
    notes: str = "",
) -> dict:
    """Buy/add shares of a stock to portfolio."""
    _ensure_db()
    trade_date = trade_date or date.today().isoformat()
    result = add_transaction(ticker, "buy", shares, price, trade_date, notes)
    return {"status": "success", "action": "buy", "position": result}


def sell_position(
    ticker: str,
    shares: float,
    price: float,
    trade_date: str | None = None,
    notes: str = "",
) -> dict:
    """Sell shares of a stock from portfolio."""
    _ensure_db()
    trade_date = trade_date or date.today().isoformat()
    try:
        result = add_transaction(ticker, "sell", shares, price, trade_date, notes)
        return {"status": "success", "action": "sell", "result": result}
    except ValueError as e:
        return {"status": "error", "message": str(e)}


def get_portfolio() -> dict:
    """Get all positions with current market prices and P&L."""
    _ensure_db()
    positions = get_positions()
    if not positions:
        return {"positions": [], "total_cost": 0, "total_market_value": 0, "total_return_pct": 0, "position_count": 0}

    enriched = []
    total_cost = 0.0
    total_market_value = 0.0

    for pos in positions:
        ticker = pos["ticker"]
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
        except Exception:
            current_price = 0

        market_value = pos["shares"] * current_price
        cost_basis = pos["total_cost"]
        pnl = market_value - cost_basis
        pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0

        enriched.append({
            **pos,
            "current_price": current_price,
            "market_value": round(market_value, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
        })

        total_cost += cost_basis
        total_market_value += market_value

    total_return = total_market_value - total_cost
    total_return_pct = (total_return / total_cost * 100) if total_cost > 0 else 0

    return {
        "positions": enriched,
        "total_cost": round(total_cost, 2),
        "total_market_value": round(total_market_value, 2),
        "total_return": round(total_return, 2),
        "total_return_pct": round(total_return_pct, 2),
        "position_count": len(enriched),
    }


def get_transaction_history(ticker: str | None = None, limit: int = 50) -> dict:
    """Get transaction history, optionally filtered by ticker."""
    _ensure_db()
    txns = get_transactions(ticker, limit)
    return {"transactions": txns, "count": len(txns)}


def get_portfolio_performance() -> dict:
    """Get portfolio performance summary with per-position breakdown."""
    portfolio = get_portfolio()
    if not portfolio["positions"]:
        return {"message": "持仓为空，暂无业绩数据"}

    # Sort by P&L descending
    winners = sorted(
        [p for p in portfolio["positions"] if p["pnl"] > 0],
        key=lambda x: x["pnl"],
        reverse=True,
    )
    losers = sorted(
        [p for p in portfolio["positions"] if p["pnl"] < 0],
        key=lambda x: x["pnl"],
    )

    return {
        "total_cost": portfolio["total_cost"],
        "total_market_value": portfolio["total_market_value"],
        "total_return": portfolio["total_return"],
        "total_return_pct": portfolio["total_return_pct"],
        "position_count": portfolio["position_count"],
        "winners": [{"ticker": p["ticker"], "pnl": p["pnl"], "pnl_pct": p["pnl_pct"]} for p in winners],
        "losers": [{"ticker": p["ticker"], "pnl": p["pnl"], "pnl_pct": p["pnl_pct"]} for p in losers],
    }


# Claude API tool definitions
PORTFOLIO_TOOLS = [
    {
        "name": "add_position",
        "description": "买入/加仓股票。记录交易并更新持仓（加权平均成本）。",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "股票代码，如 AAPL"},
                "shares": {"type": "number", "description": "买入股数"},
                "price": {"type": "number", "description": "买入价格（美元）"},
                "trade_date": {"type": "string", "description": "交易日期 YYYY-MM-DD，默认今天"},
                "notes": {"type": "string", "description": "交易备注"},
            },
            "required": ["ticker", "shares", "price"],
        },
    },
    {
        "name": "sell_position",
        "description": "卖出/减仓股票。记录交易并更新持仓。",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "股票代码"},
                "shares": {"type": "number", "description": "卖出股数"},
                "price": {"type": "number", "description": "卖出价格（美元）"},
                "trade_date": {"type": "string", "description": "交易日期 YYYY-MM-DD，默认今天"},
                "notes": {"type": "string", "description": "交易备注"},
            },
            "required": ["ticker", "shares", "price"],
        },
    },
    {
        "name": "get_portfolio",
        "description": "获取完整持仓列表，包含实时市值、盈亏金额和盈亏百分比。",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_transaction_history",
        "description": "查询交易记录，可按股票代码筛选。",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "股票代码（可选，不填则返回所有）"},
                "limit": {"type": "integer", "description": "返回条数上限，默认 50"},
            },
        },
    },
    {
        "name": "get_portfolio_performance",
        "description": "获取持仓业绩汇总：总回报、各持仓盈亏排行。",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]

PORTFOLIO_DISPATCH = {
    "add_position": add_position,
    "sell_position": sell_position,
    "get_portfolio": get_portfolio,
    "get_transaction_history": get_transaction_history,
    "get_portfolio_performance": get_portfolio_performance,
}
