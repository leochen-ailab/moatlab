"""FinancialAgent — Deep financial analysis using value investing principles."""

from __future__ import annotations

from pathlib import Path

from moatlab.agents.base import BaseAgent
from moatlab.tools.market_data import MARKET_DATA_DISPATCH, MARKET_DATA_TOOLS


_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "financial.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


class FinancialAgent(BaseAgent):
    """Analyzes a company's financial health: profitability, cash flow, balance sheet, growth."""

    def __init__(self, model: str | None = None):
        super().__init__(
            name="FinancialAgent",
            system_prompt=_load_prompt(),
            tools=MARKET_DATA_TOOLS,
            tool_dispatch=MARKET_DATA_DISPATCH,
            model=model,
        )

    def analyze(self, ticker: str) -> str:
        """Run financial analysis for a given stock ticker."""
        return self.run(f"请对 {ticker} 进行深度财务分析。")
