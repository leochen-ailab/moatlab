"""Stock screening tool — filter stocks by value investing criteria."""

from __future__ import annotations

import json
import logging

import yfinance as yf

logger = logging.getLogger(__name__)

# S&P 500 representative tickers by sector (curated for value investing screening)
# A full implementation would fetch from an index API; this is a practical starting set.
SP500_SAMPLE = [
    # Technology
    "AAPL", "MSFT", "GOOGL", "META", "AVGO", "ORCL", "CRM", "ADBE", "CSCO", "ACN",
    # Healthcare
    "UNH", "JNJ", "LLY", "ABBV", "MRK", "PFE", "TMO", "ABT", "DHR", "AMGN",
    # Financials
    "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "SPGI", "BLK",
    # Consumer Staples
    "PG", "KO", "PEP", "COST", "WMT", "PM", "MO", "CL", "KHC", "GIS",
    # Consumer Discretionary
    "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "TJX", "LOW", "BKNG", "CMG",
    # Industrials
    "CAT", "UNP", "HON", "UPS", "RTX", "DE", "GE", "LMT", "MMM", "WM",
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
    # Utilities & Real Estate
    "NEE", "DUK", "SO", "D", "AEP", "AMT", "PLD", "CCI", "EQIX", "SPG",
    # Communication
    "DIS", "CMCSA", "NFLX", "T", "VZ", "TMUS", "CHTR", "EA", "WBD", "PARA",
]


def screen_stocks(
    tickers: list[str] | None = None,
    roe_min: float | None = None,
    debt_to_equity_max: float | None = None,
    gross_margin_min: float | None = None,
    pe_max: float | None = None,
    market_cap_min: float | None = None,
    dividend_yield_min: float | None = None,
    sector: str | None = None,
    limit: int = 20,
) -> dict:
    """Screen stocks based on value investing criteria.

    Returns a list of stocks that pass all specified filters, sorted by ROE descending.
    """
    candidates = tickers or SP500_SAMPLE
    results = []
    errors = []

    for ticker in candidates:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info or not info.get("marketCap"):
                continue

            row = {
                "ticker": ticker,
                "name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "market_cap": info.get("marketCap"),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "pe_ratio": info.get("trailingPE"),
                "roe": info.get("returnOnEquity"),
                "debt_to_equity": info.get("debtToEquity"),
                "gross_margin": info.get("grossMargins"),
                "net_margin": info.get("profitMargins"),
                "dividend_yield": info.get("dividendYield"),
                "free_cash_flow": info.get("freeCashflow"),
                "revenue_growth": info.get("revenueGrowth"),
            }

            # Apply filters
            if sector and row["sector"] and sector.lower() not in row["sector"].lower():
                continue
            if roe_min is not None and (row["roe"] is None or row["roe"] < roe_min):
                continue
            if debt_to_equity_max is not None and row["debt_to_equity"] is not None and row["debt_to_equity"] > debt_to_equity_max:
                continue
            if gross_margin_min is not None and (row["gross_margin"] is None or row["gross_margin"] < gross_margin_min):
                continue
            if pe_max is not None and (row["pe_ratio"] is None or row["pe_ratio"] > pe_max):
                continue
            if market_cap_min is not None and (row["market_cap"] is None or row["market_cap"] < market_cap_min):
                continue
            if dividend_yield_min is not None and (row["dividend_yield"] is None or row["dividend_yield"] < dividend_yield_min):
                continue

            results.append(row)
        except Exception as e:
            errors.append({"ticker": ticker, "error": str(e)})
            logger.debug(f"Screener skip {ticker}: {e}")

    # Sort by ROE descending (None values last)
    results.sort(key=lambda x: x.get("roe") or 0, reverse=True)

    return {
        "total_scanned": len(candidates),
        "matches": len(results),
        "stocks": results[:limit],
        "filters_applied": {
            k: v for k, v in {
                "roe_min": roe_min,
                "debt_to_equity_max": debt_to_equity_max,
                "gross_margin_min": gross_margin_min,
                "pe_max": pe_max,
                "market_cap_min": market_cap_min,
                "dividend_yield_min": dividend_yield_min,
                "sector": sector,
            }.items() if v is not None
        },
        "errors_count": len(errors),
    }


# Tool definition for Claude API tool_use
SCREENER_TOOLS = [
    {
        "name": "screen_stocks",
        "description": "按价值投资标准筛选股票。可设置 ROE 下限、负债率上限、毛利率下限、PE 上限等条件，从 S&P 500 代表性股票中筛选。",
        "input_schema": {
            "type": "object",
            "properties": {
                "roe_min": {
                    "type": "number",
                    "description": "ROE 最低要求（小数），如 0.15 表示 15%",
                },
                "debt_to_equity_max": {
                    "type": "number",
                    "description": "负债权益比上限，如 50 表示 50%",
                },
                "gross_margin_min": {
                    "type": "number",
                    "description": "毛利率最低要求（小数），如 0.4 表示 40%",
                },
                "pe_max": {
                    "type": "number",
                    "description": "PE 上限，如 25",
                },
                "market_cap_min": {
                    "type": "number",
                    "description": "最低市值（美元），如 10000000000 表示 100 亿",
                },
                "dividend_yield_min": {
                    "type": "number",
                    "description": "最低股息率（小数），如 0.02 表示 2%",
                },
                "sector": {
                    "type": "string",
                    "description": "行业筛选，如 Technology, Healthcare, Consumer",
                },
                "limit": {
                    "type": "integer",
                    "description": "返回结果上限，默认 20",
                    "default": 20,
                },
            },
        },
    },
]

SCREENER_DISPATCH = {
    "screen_stocks": screen_stocks,
}
