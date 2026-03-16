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


def get_cash_flow_summary(ticker: str) -> dict:
    """Get key cash flow metrics directly extracted from cash flow statement.

    Returns clean, ready-to-use values for DCF and Owner Earnings calculations.
    Avoids Agent confusion by extracting specific line items.
    """
    stock = yf.Ticker(ticker)
    cf = stock.cashflow

    if cf is None or cf.empty:
        return {"ticker": ticker, "error": "No cash flow data available"}

    # Get the most recent 4 fiscal years (columns are sorted newest to oldest)
    years = []
    for col in cf.columns[:4]:  # Take up to 4 most recent years
        year_label = col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)

        # Extract key metrics
        fcf = _safe_value(cf.loc["Free Cash Flow", col]) if "Free Cash Flow" in cf.index else None
        operating_cf = _safe_value(cf.loc["Operating Cash Flow", col]) if "Operating Cash Flow" in cf.index else None

        # CapEx: use "Capital Expenditure" or "Purchase Of PPE" (NOT Investing Cash Flow)
        capex_raw = None
        if "Capital Expenditure" in cf.index:
            capex_raw = _safe_value(cf.loc["Capital Expenditure", col])
        elif "Purchase Of PPE" in cf.index:
            capex_raw = _safe_value(cf.loc["Purchase Of PPE", col])
        # Convert to positive number (yfinance reports as negative)
        capex = abs(capex_raw) if capex_raw is not None else None

        # Depreciation
        depreciation = None
        if "Depreciation And Amortization" in cf.index:
            depreciation = _safe_value(cf.loc["Depreciation And Amortization", col])
        elif "Depreciation Amortization Depletion" in cf.index:
            depreciation = _safe_value(cf.loc["Depreciation Amortization Depletion", col])

        # Working Capital Change (negative = cash outflow = increase in WC)
        wc_change_raw = _safe_value(cf.loc["Change In Working Capital", col]) if "Change In Working Capital" in cf.index else None
        # Convert to "working capital increase" (positive = cash used)
        wc_increase = -wc_change_raw if wc_change_raw is not None else None

        years.append({
            "fiscal_year": year_label,
            "free_cash_flow": fcf,
            "operating_cash_flow": operating_cf,
            "capex": capex,
            "depreciation": depreciation,
            "working_capital_increase": wc_increase,
        })

    # Cross-validation: FCF should ≈ Operating CF - CapEx
    validation_notes = []
    for year_data in years:
        if all(year_data.get(k) is not None for k in ["free_cash_flow", "operating_cash_flow", "capex"]):
            calculated_fcf = year_data["operating_cash_flow"] - year_data["capex"]
            reported_fcf = year_data["free_cash_flow"]
            diff_pct = abs(calculated_fcf - reported_fcf) / reported_fcf if reported_fcf != 0 else 0
            if diff_pct > 0.05:  # >5% difference
                validation_notes.append(
                    f"{year_data['fiscal_year']}: FCF validation warning - "
                    f"reported {reported_fcf/1e9:.1f}B vs calculated {calculated_fcf/1e9:.1f}B"
                )

    return {
        "ticker": ticker,
        "years": years,
        "validation_notes": validation_notes if validation_notes else ["All FCF values validated"],
        "usage_note": (
            "Use 'free_cash_flow' for DCF. "
            "For Owner Earnings: use net_income + depreciation - capex - working_capital_increase. "
            "All values in original currency (USD for US stocks)."
        ),
    }


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
    {
        "name": "get_cash_flow_summary",
        "description": (
            "获取现金流关键指标摘要（最近4年）。"
            "直接提取 FCF、Operating CF、CapEx、Depreciation、Working Capital 变动。"
            "用于 DCF 和 Owner Earnings 计算，避免从完整财报中误读数据。"
            "包含交叉验证：FCF ≈ Operating CF - CapEx。"
        ),
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
]

# Function dispatch map
MARKET_DATA_DISPATCH = {
    "get_stock_info": get_stock_info,
    "get_financial_statements": get_financial_statements,
    "get_key_metrics": get_key_metrics,
    "get_historical_prices": get_historical_prices,
    "get_cash_flow_summary": get_cash_flow_summary,
}
