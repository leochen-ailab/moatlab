"""Market data tool — yfinance wrapper for stock data retrieval."""

from __future__ import annotations

import json

import yfinance as yf


def get_stock_info(ticker: str) -> dict:
    """Get basic stock info: price, market cap, sector, etc."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "name": info.get("longName", ""),
        "sector": info.get("sector", ""),
        "industry": info.get("industry", ""),
        "market_cap": info.get("marketCap"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "currency": info.get("currency", "USD"),
        "exchange": info.get("exchange", ""),
        "description": info.get("longBusinessSummary", ""),
    }


def get_financial_statements(ticker: str) -> dict:
    """Get income statement, balance sheet, and cash flow (annual, last 4 years)."""
    stock = yf.Ticker(ticker)

    def df_to_dict(df):
        if df is None or df.empty:
            return {}
        result = {}
        for col in df.columns:
            col_key = col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)
            result[col_key] = {
                str(idx): _safe_value(val) for idx, val in df[col].items()
            }
        return result

    return {
        "income_statement": df_to_dict(stock.income_stmt),
        "balance_sheet": df_to_dict(stock.balance_sheet),
        "cash_flow": df_to_dict(stock.cashflow),
    }


def get_key_metrics(ticker: str) -> dict:
    """Get key financial ratios and metrics."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "pb_ratio": info.get("priceToBook"),
        "ps_ratio": info.get("priceToSalesTrailing12Months"),
        "dividend_yield": info.get("dividendYield"),
        "payout_ratio": info.get("payoutRatio"),
        "roe": info.get("returnOnEquity"),
        "roa": info.get("returnOnAssets"),
        "debt_to_equity": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "gross_margins": info.get("grossMargins"),
        "operating_margins": info.get("operatingMargins"),
        "profit_margins": info.get("profitMargins"),
        "free_cash_flow": info.get("freeCashflow"),
        "operating_cash_flow": info.get("operatingCashflow"),
        "total_revenue": info.get("totalRevenue"),
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
    }


def get_historical_prices(ticker: str, period: str = "5y") -> dict:
    """Get historical price data for valuation context."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if hist.empty:
        return {"ticker": ticker, "prices": []}

    # Resample to monthly for manageable size
    monthly = hist["Close"].resample("ME").last()
    prices = [
        {"date": d.strftime("%Y-%m-%d"), "close": round(v, 2)}
        for d, v in monthly.items()
        if v == v  # skip NaN
    ]
    return {"ticker": ticker, "period": period, "monthly_prices": prices}


def _safe_value(val) -> float | None:
    """Convert numpy/pandas values to Python native types."""
    if val is None:
        return None
    try:
        f = float(val)
        return None if f != f else f  # NaN check
    except (ValueError, TypeError):
        return None


# Tool definitions for Claude API tool_use
MARKET_DATA_TOOLS = [
    {
        "name": "get_stock_info",
        "description": "获取股票基本信息：公司名称、行业、市值、当前价格、业务描述等。用于了解公司是什么、做什么生意。",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "股票代码，如 AAPL, MSFT, KO",
                }
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_financial_statements",
        "description": "获取公司最近4年的三大财务报表（利润表、资产负债表、现金流量表）。用于深度财务分析。",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "股票代码",
                }
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_key_metrics",
        "description": "获取关键财务指标：PE、PB、ROE、负债率、毛利率、净利率、自由现金流等。用于快速评估财务健康状况。",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "股票代码",
                }
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_historical_prices",
        "description": "获取股票历史月度价格数据。用于估值对比和趋势分析。",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "股票代码",
                },
                "period": {
                    "type": "string",
                    "description": "时间范围，如 1y, 3y, 5y, 10y",
                    "default": "5y",
                },
            },
            "required": ["ticker"],
        },
    },
]

# Function dispatch map
MARKET_DATA_DISPATCH = {
    "get_stock_info": get_stock_info,
    "get_financial_statements": get_financial_statements,
    "get_key_metrics": get_key_metrics,
    "get_historical_prices": get_historical_prices,
}
