"""Data models for stock analysis reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class MoatType(str, Enum):
    BRAND = "brand"
    NETWORK_EFFECTS = "network_effects"
    SWITCHING_COSTS = "switching_costs"
    COST_ADVANTAGES = "cost_advantages"
    ECONOMIES_OF_SCALE = "economies_of_scale"
    INTANGIBLE_ASSETS = "intangible_assets"


class Recommendation(str, Enum):
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    PASS = "pass"  # 不懂不做


@dataclass
class FinancialMetrics:
    """Key financial metrics for a stock."""

    ticker: str
    revenue: float | None = None
    net_income: float | None = None
    free_cash_flow: float | None = None
    owner_earnings: float | None = None
    roe: float | None = None
    roic: float | None = None
    debt_to_equity: float | None = None
    gross_margin: float | None = None
    net_margin: float | None = None
    interest_coverage: float | None = None
    # 趋势数据 (近5年)
    revenue_growth_5y: list[float] = field(default_factory=list)
    fcf_history_5y: list[float] = field(default_factory=list)
    roe_history_5y: list[float] = field(default_factory=list)


@dataclass
class ValuationResult:
    """Valuation output with intrinsic value and margin of safety."""

    ticker: str
    current_price: float
    intrinsic_value_dcf: float | None = None
    intrinsic_value_owner_earnings: float | None = None
    pe_ratio: float | None = None
    pb_ratio: float | None = None
    pe_percentile_5y: float | None = None  # 当前PE在5年历史中的分位
    margin_of_safety: float | None = None  # 安全边际百分比


@dataclass
class AnalysisReport:
    """Complete analysis report for a stock."""

    ticker: str
    company_name: str = ""
    financial_summary: str = ""
    valuation_summary: str = ""
    metrics: FinancialMetrics | None = None
    valuation: ValuationResult | None = None
    recommendation: Recommendation = Recommendation.PASS
    reasoning: str = ""
    risks: list[str] = field(default_factory=list)  # 段永平: 反过来想
