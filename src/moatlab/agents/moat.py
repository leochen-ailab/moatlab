"""MoatAgent — Competitive advantage (moat) analysis."""

from __future__ import annotations

from pathlib import Path

from moatlab.agents.base import BaseAgent
from moatlab.tools.market_data import MARKET_DATA_DISPATCH, MARKET_DATA_TOOLS


_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "moat.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


class MoatAgent(BaseAgent):
    """Analyzes a company's competitive moat: brand, network effects, switching costs, etc."""

    def __init__(self, model: str | None = None):
        super().__init__(
            name="MoatAgent",
            system_prompt=_load_prompt(),
            tools=MARKET_DATA_TOOLS,
            tool_dispatch=MARKET_DATA_DISPATCH,
            model=model,
        )

    def analyze(self, ticker: str) -> str:
        """Run moat analysis for a given stock ticker."""
        return self.run(f"请对 {ticker} 进行护城河分析，评估其竞争优势的类型、强度和持久性。")
