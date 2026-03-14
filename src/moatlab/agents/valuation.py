"""ValuationAgent — Intrinsic value calculation and margin of safety assessment."""

from __future__ import annotations

from pathlib import Path

from moatlab.agents.base import BaseAgent
from moatlab.tools.calculator import CALCULATOR_DISPATCH, CALCULATOR_TOOLS
from moatlab.tools.market_data import MARKET_DATA_DISPATCH, MARKET_DATA_TOOLS


_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "valuation.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


class ValuationAgent(BaseAgent):
    """Calculates intrinsic value using DCF, Owner Earnings, and relative valuation."""

    def __init__(self, model: str | None = None):
        # Combine market data tools and calculator tools
        all_tools = MARKET_DATA_TOOLS + CALCULATOR_TOOLS
        all_dispatch = {**MARKET_DATA_DISPATCH, **CALCULATOR_DISPATCH}

        super().__init__(
            name="ValuationAgent",
            system_prompt=_load_prompt(),
            tools=all_tools,
            tool_dispatch=all_dispatch,
            model=model,
        )

    def analyze(self, ticker: str) -> str:
        """Run valuation analysis for a given stock ticker."""
        return self.run(f"请对 {ticker} 进行估值分析，计算内在价值和安全边际。")
