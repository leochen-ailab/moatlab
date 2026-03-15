"""Orchestrator — Coordinates multiple agents for full analysis pipeline."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from moatlab.agents.decision import DecisionAgent
from moatlab.agents.financial import FinancialAgent
from moatlab.agents.management import ManagementAgent
from moatlab.agents.moat import MoatAgent
from moatlab.agents.valuation import ValuationAgent

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrates the full value investing analysis pipeline.

    Execution flow (DAG):
        ┌─── MoatAgent ───────┐
        ├─── ManagementAgent ──┤  (parallel)
        ├─── FinancialAgent ───┤
        │                      ▼
        │              ValuationAgent  (depends on FinancialAgent context)
        │                      │
        └──────────────────────▼
                        DecisionAgent  (aggregates all reports)
    """

    def __init__(self, model: str | None = None):
        self.model = model

    def analyze(
        self,
        ticker: str,
        on_progress: callable | None = None,
    ) -> dict[str, str]:
        """Run full analysis pipeline for a stock.

        Args:
            ticker: Stock ticker symbol.
            on_progress: Optional callback(agent_name, status) for progress updates.

        Returns:
            Dict with keys: moat, management, financial, valuation, decision, and each value is the report text.
        """
        reports: dict[str, str] = {}

        def _notify(agent_name: str, status: str):
            if on_progress:
                on_progress(agent_name, status)

        # Phase 1: Run moat, management, financial in parallel
        _notify("Phase 1", "并行分析护城河、管理层、财务...")

        phase1_agents = {
            "moat": MoatAgent(model=self.model),
            "management": ManagementAgent(model=self.model),
            "financial": FinancialAgent(model=self.model),
        }

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            for name, agent in phase1_agents.items():
                _notify(name, "开始分析")
                futures[executor.submit(agent.analyze, ticker)] = name

            for future in as_completed(futures):
                name = futures[future]
                try:
                    reports[name] = future.result()
                    _notify(name, "完成")
                    logger.info(f"[Orchestrator] {name} 分析完成")
                except Exception as e:
                    reports[name] = f"分析失败: {e}"
                    _notify(name, f"失败: {e}")
                    logger.error(f"[Orchestrator] {name} 分析失败: {e}")

        # Phase 2: Valuation (sequential, benefits from separate financial context)
        _notify("valuation", "开始估值分析")
        try:
            valuation_agent = ValuationAgent(model=self.model)
            reports["valuation"] = valuation_agent.analyze(ticker)
            _notify("valuation", "完成")
        except Exception as e:
            reports["valuation"] = f"估值分析失败: {e}"
            _notify("valuation", f"失败: {e}")

        # Phase 3: Decision (aggregates all reports)
        _notify("decision", "综合决策中...")
        try:
            decision_agent = DecisionAgent(model=self.model)
            reports["decision"] = decision_agent.decide(ticker, {
                "护城河": reports.get("moat", "无数据"),
                "管理层": reports.get("management", "无数据"),
                "财务": reports.get("financial", "无数据"),
                "估值": reports.get("valuation", "无数据"),
            })
            _notify("decision", "完成")
        except Exception as e:
            reports["decision"] = f"决策分析失败: {e}"
            _notify("decision", f"失败: {e}")

        return reports
