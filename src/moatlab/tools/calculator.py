"""DCF and valuation calculator tools."""

from __future__ import annotations


def calculate_dcf(
    free_cash_flows: list[float],
    growth_rate: float = 0.05,
    terminal_growth_rate: float = 0.03,
    discount_rate: float = 0.10,
    projection_years: int = 10,
    shares_outstanding: float | None = None,
) -> dict:
    """Calculate intrinsic value using Discounted Cash Flow model.

    Uses the most recent FCF as base, projects forward, and discounts back.
    Terminal value uses Gordon Growth Model.
    """
    if not free_cash_flows or all(f <= 0 for f in free_cash_flows):
        return {"error": "No positive free cash flow data available for DCF"}

    # Use average of recent FCFs as base (more stable than single year)
    positive_fcfs = [f for f in free_cash_flows if f > 0]
    base_fcf = sum(positive_fcfs) / len(positive_fcfs)

    # Project future cash flows
    projected_fcfs = []
    for year in range(1, projection_years + 1):
        projected = base_fcf * (1 + growth_rate) ** year
        projected_fcfs.append(projected)

    # Discount projected cash flows
    discounted_fcfs = []
    for year, fcf in enumerate(projected_fcfs, 1):
        discounted = fcf / (1 + discount_rate) ** year
        discounted_fcfs.append(discounted)

    # Terminal value (Gordon Growth Model)
    terminal_fcf = projected_fcfs[-1] * (1 + terminal_growth_rate)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
    discounted_terminal = terminal_value / (1 + discount_rate) ** projection_years

    # Total intrinsic value
    total_value = sum(discounted_fcfs) + discounted_terminal

    result = {
        "base_fcf": round(base_fcf, 2),
        "growth_rate": growth_rate,
        "discount_rate": discount_rate,
        "terminal_growth_rate": terminal_growth_rate,
        "projection_years": projection_years,
        "sum_discounted_fcfs": round(sum(discounted_fcfs), 2),
        "discounted_terminal_value": round(discounted_terminal, 2),
        "intrinsic_value_total": round(total_value, 2),
    }

    if shares_outstanding and shares_outstanding > 0:
        result["intrinsic_value_per_share"] = round(total_value / shares_outstanding, 2)

    return result


def calculate_owner_earnings(
    net_income: float,
    depreciation: float,
    capex: float,
    working_capital_change: float = 0,
) -> dict:
    """Calculate Owner Earnings (Buffett's preferred measure).

    Owner Earnings = Net Income + Depreciation - CapEx - Working Capital Changes
    """
    owner_earnings = net_income + depreciation - abs(capex) - working_capital_change
    return {
        "net_income": net_income,
        "depreciation": depreciation,
        "capex": capex,
        "working_capital_change": working_capital_change,
        "owner_earnings": round(owner_earnings, 2),
    }


def calculate_margin_of_safety(
    current_price: float,
    intrinsic_value: float,
) -> dict:
    """Calculate margin of safety percentage."""
    if intrinsic_value <= 0:
        return {
            "current_price": current_price,
            "intrinsic_value": intrinsic_value,
            "margin_of_safety": None,
            "verdict": "无法计算：内在价值为负",
        }

    mos = (intrinsic_value - current_price) / intrinsic_value
    if mos >= 0.30:
        verdict = "安全边际充足 (≥30%)，具备买入条件"
    elif mos >= 0.15:
        verdict = "安全边际一般 (15-30%)，可关注等待更好价格"
    elif mos >= 0:
        verdict = "安全边际不足 (<15%)，价格偏贵"
    else:
        verdict = "当前价格高于内在价值，不建议买入"

    return {
        "current_price": current_price,
        "intrinsic_value": round(intrinsic_value, 2),
        "margin_of_safety": round(mos, 4),
        "margin_of_safety_pct": f"{mos * 100:.1f}%",
        "verdict": verdict,
    }


# Tool definitions for Claude API tool_use
CALCULATOR_TOOLS = [
    {
        "name": "calculate_dcf",
        "description": "使用自由现金流折现模型（DCF）计算公司内在价值。输入历史FCF、增长率假设、折现率等参数。",
        "input_schema": {
            "type": "object",
            "properties": {
                "free_cash_flows": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "近几年的自由现金流列表（从旧到新），单位与财报一致",
                },
                "growth_rate": {
                    "type": "number",
                    "description": "预期年增长率，如 0.05 表示 5%",
                    "default": 0.05,
                },
                "terminal_growth_rate": {
                    "type": "number",
                    "description": "永续增长率，通常 2-3%",
                    "default": 0.03,
                },
                "discount_rate": {
                    "type": "number",
                    "description": "折现率，通常 8-12%",
                    "default": 0.10,
                },
                "projection_years": {
                    "type": "integer",
                    "description": "预测年数",
                    "default": 10,
                },
                "shares_outstanding": {
                    "type": "number",
                    "description": "流通股数量，用于计算每股内在价值",
                },
            },
            "required": ["free_cash_flows"],
        },
    },
    {
        "name": "calculate_owner_earnings",
        "description": "计算巴菲特式 Owner Earnings（所有者盈余）= 净利润 + 折旧 - 资本支出 - 营运资本变动。",
        "input_schema": {
            "type": "object",
            "properties": {
                "net_income": {"type": "number", "description": "净利润"},
                "depreciation": {"type": "number", "description": "折旧和摊销"},
                "capex": {"type": "number", "description": "资本支出（正数）"},
                "working_capital_change": {
                    "type": "number",
                    "description": "营运资本变动",
                    "default": 0,
                },
            },
            "required": ["net_income", "depreciation", "capex"],
        },
    },
    {
        "name": "calculate_margin_of_safety",
        "description": "计算安全边际。对比当前价格与内在价值，判断是否具备买入条件（目标≥30%）。",
        "input_schema": {
            "type": "object",
            "properties": {
                "current_price": {"type": "number", "description": "当前股价"},
                "intrinsic_value": {"type": "number", "description": "内在价值估算"},
            },
            "required": ["current_price", "intrinsic_value"],
        },
    },
]

CALCULATOR_DISPATCH = {
    "calculate_dcf": calculate_dcf,
    "calculate_owner_earnings": calculate_owner_earnings,
    "calculate_margin_of_safety": calculate_margin_of_safety,
}
