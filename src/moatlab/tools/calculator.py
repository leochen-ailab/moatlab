"""DCF and valuation calculator tools."""

from __future__ import annotations


def calculate_sensitivity_matrix(
    base_fcf: float,
    shares_outstanding: float,
    growth_rates: list[float],
    discount_rates: list[float],
    terminal_growth_rate: float = 0.03,
    projection_years: int = 10,
    base_fcf_method: str = "latest",
) -> dict:
    """Calculate sensitivity matrix showing intrinsic value per share across different scenarios.

    Args:
        base_fcf: Starting free cash flow
        shares_outstanding: Diluted shares outstanding
        growth_rates: List of growth rates to test (e.g., [0.05, 0.06, 0.08, 0.10])
        discount_rates: List of discount rates to test (e.g., [0.09, 0.10, 0.11])
        terminal_growth_rate: Perpetual growth rate
        projection_years: Forecast period
        base_fcf_method: FCF selection method

    Returns:
        Dict with matrix data and formatted table
    """
    matrix = []

    for discount_rate in discount_rates:
        row = {"discount_rate": discount_rate, "values": []}
        for growth_rate in growth_rates:
            result = calculate_dcf(
                free_cash_flows=[base_fcf],
                growth_rate=growth_rate,
                terminal_growth_rate=terminal_growth_rate,
                discount_rate=discount_rate,
                projection_years=projection_years,
                shares_outstanding=shares_outstanding,
                base_fcf_method=base_fcf_method,
            )
            per_share = result.get("intrinsic_value_per_share", 0)
            row["values"].append(round(per_share, 2))
        matrix.append(row)

    return {
        "base_fcf": base_fcf,
        "shares_outstanding": shares_outstanding,
        "growth_rates": growth_rates,
        "discount_rates": discount_rates,
        "terminal_growth_rate": terminal_growth_rate,
        "matrix": matrix,
        "interpretation": (
            "敏感性矩阵展示估值对关键参数的敏感性。"
            "横轴=增长率，纵轴=折现率。"
            "如果估值在小幅参数变化下波动剧烈，说明估值脆弱。"
        ),
    }


def calculate_dcf_two_stage(
    base_fcf: float,
    high_growth_rate: float,
    high_growth_years: int,
    terminal_growth_rate: float = 0.03,
    discount_rate: float = 0.10,
    transition_years: int = 5,
    shares_outstanding: float | None = None,
    net_cash: float = 0,
) -> dict:
    """Calculate intrinsic value using Two-Stage DCF model.

    Stage 1: High growth period (e.g., Y1-5 at 15%)
    Stage 2: Transition period (e.g., Y6-10, linear decline to terminal rate)
    Terminal: Perpetual growth at terminal_growth_rate

    Args:
        base_fcf: Starting free cash flow
        high_growth_rate: Growth rate for high growth period (e.g., 0.15 for 15%)
        high_growth_years: Duration of high growth period (e.g., 5)
        terminal_growth_rate: Perpetual growth rate (e.g., 0.03 for 3%)
        discount_rate: WACC (e.g., 0.10 for 10%)
        transition_years: Years to transition from high growth to terminal (e.g., 5)
        shares_outstanding: Diluted shares outstanding
        net_cash: Net cash (cash - debt) to add to enterprise value

    Returns:
        Dict with intrinsic value, stage breakdown, and detailed cash flows
    """
    projected_fcfs = []
    stage_labels = []

    # Stage 1: High growth period
    current_fcf = base_fcf
    for year in range(1, high_growth_years + 1):
        current_fcf = current_fcf * (1 + high_growth_rate)
        projected_fcfs.append(current_fcf)
        stage_labels.append(f"Y{year} (高增长)")

    # Stage 2: Transition period (linear decline from high_growth_rate to terminal_growth_rate)
    growth_decline_per_year = (high_growth_rate - terminal_growth_rate) / transition_years
    for year in range(1, transition_years + 1):
        transition_growth = high_growth_rate - (growth_decline_per_year * year)
        current_fcf = current_fcf * (1 + transition_growth)
        projected_fcfs.append(current_fcf)
        stage_labels.append(f"Y{high_growth_years + year} (回落期)")

    # Discount all projected cash flows
    discounted_fcfs = []
    for year, fcf in enumerate(projected_fcfs, 1):
        discounted = fcf / (1 + discount_rate) ** year
        discounted_fcfs.append(discounted)

    # Terminal value (Gordon Growth Model)
    total_years = high_growth_years + transition_years
    terminal_fcf = projected_fcfs[-1] * (1 + terminal_growth_rate)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
    discounted_terminal = terminal_value / (1 + discount_rate) ** total_years

    # Total intrinsic value
    operating_value = sum(discounted_fcfs) + discounted_terminal
    total_value = operating_value + net_cash

    # Stage breakdown for transparency
    stage1_pv = sum(discounted_fcfs[:high_growth_years])
    stage2_pv = sum(discounted_fcfs[high_growth_years:])

    result = {
        "model": "two_stage_dcf",
        "base_fcf": round(base_fcf, 2),
        "high_growth_rate": high_growth_rate,
        "high_growth_years": high_growth_years,
        "terminal_growth_rate": terminal_growth_rate,
        "discount_rate": discount_rate,
        "transition_years": transition_years,
        "net_cash": round(net_cash, 2),
        "stage1_pv": round(stage1_pv, 2),
        "stage2_pv": round(stage2_pv, 2),
        "discounted_terminal_value": round(discounted_terminal, 2),
        "intrinsic_value_total": round(total_value, 2),
        "cash_flow_details": [
            {
                "year": i + 1,
                "stage": stage_labels[i],
                "projected_fcf": round(fcf, 2),
                "discounted_fcf": round(discounted_fcfs[i], 2),
            }
            for i, fcf in enumerate(projected_fcfs)
        ],
    }

    if shares_outstanding and shares_outstanding > 0:
        result["intrinsic_value_per_share"] = round(total_value / shares_outstanding, 2)

    return result


def calculate_dcf(
    free_cash_flows: list[float],
    growth_rate: float = 0.05,
    terminal_growth_rate: float = 0.03,
    discount_rate: float = 0.10,
    projection_years: int = 10,
    shares_outstanding: float | None = None,
    base_fcf_method: str = "latest",
    net_cash: float = 0,
) -> dict:
    """Calculate intrinsic value using Discounted Cash Flow model.

    base_fcf_method:
      - "latest": use the most recent year's FCF (default, suits high-growth)
      - "average": simple average of all positive FCFs
      - "weighted": weighted average, recent years get higher weight (3-2-1)
    """
    if not free_cash_flows or all(f <= 0 for f in free_cash_flows):
        return {"error": "No positive free cash flow data available for DCF"}

    positive_fcfs = [f for f in free_cash_flows if f > 0]

    if base_fcf_method == "latest":
        # Use the last (most recent) positive FCF
        base_fcf = free_cash_flows[-1] if free_cash_flows[-1] > 0 else positive_fcfs[-1]
    elif base_fcf_method == "weighted":
        # Weighted average: recent years get higher weight
        # e.g. for 4 years: weights = [1, 2, 3, 4]
        n = len(free_cash_flows)
        weights = list(range(1, n + 1))
        weighted_sum = sum(f * w for f, w in zip(free_cash_flows, weights) if f > 0)
        weight_total = sum(w for f, w in zip(free_cash_flows, weights) if f > 0)
        base_fcf = weighted_sum / weight_total
    else:  # "average"
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

    # Total intrinsic value = operating value + net cash
    operating_value = sum(discounted_fcfs) + discounted_terminal
    total_value = operating_value + net_cash

    result = {
        "base_fcf": round(base_fcf, 2),
        "base_fcf_method": base_fcf_method,
        "growth_rate": growth_rate,
        "discount_rate": discount_rate,
        "terminal_growth_rate": terminal_growth_rate,
        "projection_years": projection_years,
        "net_cash": round(net_cash, 2),
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
    working_capital_increase: float = 0,
) -> dict:
    """Calculate Owner Earnings (Buffett's preferred measure).

    Owner Earnings = Net Income + Depreciation - CapEx - Working Capital Increase

    Args:
        net_income: 净利润（正数）
        depreciation: 折旧和摊销（正数）
        capex: 资本支出（传正数，如 6.0B 就传 6000000000）
        working_capital_increase: 营运资本增加额（正数=占用现金，负数=释放现金）。
            从现金流量表取 "Change In Working Capital" 并取反：
            若现金流量表值为 -15.9B（现金流出），则此处传 15.9B（正数，表示占用现金）。
    """
    owner_earnings = net_income + depreciation - abs(capex) - working_capital_increase
    return {
        "net_income": net_income,
        "depreciation": depreciation,
        "capex": abs(capex),
        "working_capital_increase": working_capital_increase,
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
        premium = (current_price - intrinsic_value) / intrinsic_value
        verdict = f"当前价格高于内在价值 {premium * 100:.0f}%，不建议买入"

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
        "name": "calculate_dcf_two_stage",
        "description": (
            "使用两阶段 DCF 模型计算内在价值，适合高增长公司。"
            "Stage 1: 高增长期（如 Y1-5 维持 15% 增长）"
            "Stage 2: 回落期（如 Y6-10 线性回落到永续增长率）"
            "相比单阶段 DCF，更符合公司生命周期规律。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "base_fcf": {
                    "type": "number",
                    "description": "起始自由现金流（最新年度 FCF）",
                },
                "high_growth_rate": {
                    "type": "number",
                    "description": "高增长期年增长率，如 0.15 表示 15%",
                },
                "high_growth_years": {
                    "type": "integer",
                    "description": "高增长期持续年数，通常 3-5 年",
                    "default": 5,
                },
                "terminal_growth_rate": {
                    "type": "number",
                    "description": "永续增长率，通常 2.5-3.5%",
                    "default": 0.03,
                },
                "discount_rate": {
                    "type": "number",
                    "description": "折现率（WACC），高增长公司 10-11%，成熟公司 9-10%",
                    "default": 0.10,
                },
                "transition_years": {
                    "type": "integer",
                    "description": "从高增长回落到永续增长的过渡年数，通常 5 年",
                    "default": 5,
                },
                "shares_outstanding": {
                    "type": "number",
                    "description": "总股数（稀释后），用于计算每股内在价值",
                },
                "net_cash": {
                    "type": "number",
                    "description": "净现金（现金 - 负债），用于调整企业价值到权益价值",
                    "default": 0,
                },
            },
            "required": ["base_fcf", "high_growth_rate"],
        },
    },
    {
        "name": "calculate_dcf",
        "description": (
            "使用自由现金流折现模型（DCF）计算公司内在价值。"
            "支持三种 base FCF 选择方式：latest（最新年度）、weighted（加权平均）、average（简单平均）。"
            "高增长公司建议用 latest，稳定公司用 weighted 或 average。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "free_cash_flows": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": (
                        "近几年的自由现金流列表（从旧到新），单位：美元原值。"
                        "必须使用 get_cash_flow_summary 返回的 free_cash_flow 字段，"
                        "不要自己计算或用 Investing Cash Flow 替代。"
                    ),
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
                    "description": "总股数（稀释后），用于计算每股内在价值",
                },
                "base_fcf_method": {
                    "type": "string",
                    "enum": ["latest", "weighted", "average"],
                    "description": (
                        "base FCF 选择方式。"
                        "latest=最新年度（适合高增长），"
                        "weighted=加权平均（适合中等增长），"
                        "average=简单平均（适合稳定公司）"
                    ),
                    "default": "latest",
                },
                "net_cash": {
                    "type": "number",
                    "description": "净现金（现金及等价物 - 总负债），用于调整企业价值到权益价值",
                    "default": 0,
                },
            },
            "required": ["free_cash_flows"],
        },
    },
    {
        "name": "calculate_owner_earnings",
        "description": (
            "计算巴菲特式 Owner Earnings（所有者盈余）= 净利润 + 折旧 - 资本支出 - 营运资本增加额。"
            "注意：capex 传正数；working_capital_increase 是营运资本占用的现金（正数=占用，负数=释放），"
            "取现金流量表 'Change In Working Capital' 的相反数。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "net_income": {"type": "number", "description": "净利润（正数）"},
                "depreciation": {"type": "number", "description": "折旧和摊销（正数）"},
                "capex": {
                    "type": "number",
                    "description": (
                        "资本支出（传正数）。"
                        "使用 get_cash_flow_summary 中的 capex 字段（已转为正数）。"
                        "注意：CapEx = Purchase of PPE，不是 Investing Cash Flow。"
                    ),
                },
                "working_capital_increase": {
                    "type": "number",
                    "description": (
                        "营运资本增加额。正数=占用现金（不利），负数=释放现金（有利）。"
                        "使用 get_cash_flow_summary 中的 working_capital_increase 字段。"
                    ),
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
                "intrinsic_value": {"type": "number", "description": "每股内在价值估算"},
            },
            "required": ["current_price", "intrinsic_value"],
        },
    },
    {
        "name": "calculate_sensitivity_matrix",
        "description": (
            "计算敏感性矩阵，展示估值对增长率和折现率的敏感性。"
            "用于识别估值脆弱点：如果小幅参数变化导致估值剧烈波动，说明估值不稳健。"
            "必须在报告中展示此矩阵。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "base_fcf": {
                    "type": "number",
                    "description": "起始自由现金流（最新年度 FCF）",
                },
                "shares_outstanding": {
                    "type": "number",
                    "description": "总股数（稀释后）",
                },
                "growth_rates": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "要测试的增长率列表，如 [0.05, 0.06, 0.08, 0.10]",
                },
                "discount_rates": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "要测试的折现率列表，如 [0.09, 0.10, 0.11]",
                },
                "terminal_growth_rate": {
                    "type": "number",
                    "description": "永续增长率",
                    "default": 0.03,
                },
                "projection_years": {
                    "type": "integer",
                    "description": "预测年数",
                    "default": 10,
                },
                "base_fcf_method": {
                    "type": "string",
                    "enum": ["latest", "weighted", "average"],
                    "description": "FCF 基数选择方式",
                    "default": "latest",
                },
            },
            "required": ["base_fcf", "shares_outstanding", "growth_rates", "discount_rates"],
        },
    },
]

CALCULATOR_DISPATCH = {
    "calculate_dcf_two_stage": calculate_dcf_two_stage,
    "calculate_dcf": calculate_dcf,
    "calculate_owner_earnings": calculate_owner_earnings,
    "calculate_margin_of_safety": calculate_margin_of_safety,
    "calculate_sensitivity_matrix": calculate_sensitivity_matrix,
}
