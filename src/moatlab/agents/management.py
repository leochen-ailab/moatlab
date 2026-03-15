"""ManagementAgent — Management quality analysis."""

from __future__ import annotations

from pathlib import Path

from moatlab.agents.base import BaseAgent
from moatlab.tools.market_data import MARKET_DATA_DISPATCH, MARKET_DATA_TOOLS


_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "management.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


class ManagementAgent(BaseAgent):
    """Evaluates management quality: integrity, capital allocation, shareholder alignment."""

    def __init__(self, model: str | None = None):
        super().__init__(
            name="ManagementAgent",
            system_prompt=_load_prompt(),
            tools=MARKET_DATA_TOOLS,
            tool_dispatch=MARKET_DATA_DISPATCH,
            model=model,
        )

    def analyze(self, ticker: str) -> str:
        """Run management quality analysis for a given stock ticker."""
        return self.run(f"请对 {ticker} 的管理层进行深度评估分析。")
