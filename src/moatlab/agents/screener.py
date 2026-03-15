"""ScreenerAgent — Stock screening using value investing criteria."""

from __future__ import annotations

from pathlib import Path

from moatlab.agents.base import BaseAgent
from moatlab.tools.screener import SCREENER_DISPATCH, SCREENER_TOOLS


_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "screener.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


class ScreenerAgent(BaseAgent):
    """Screens stocks based on value investing criteria and provides brief commentary."""

    def __init__(self, model: str | None = None):
        super().__init__(
            name="ScreenerAgent",
            system_prompt=_load_prompt(),
            tools=SCREENER_TOOLS,
            tool_dispatch=SCREENER_DISPATCH,
            model=model,
        )

    def screen(self, criteria: str | None = None) -> str:
        """Screen stocks with optional user-specified criteria."""
        if criteria:
            prompt = f"请按以下条件筛选股票：{criteria}"
        else:
            prompt = "请使用价值投资默认标准（ROE≥15%、毛利率≥40%）筛选股票，找出最值得深度研究的候选标的。"
        return self.run(prompt)
