"""PortfolioAgent — Portfolio management using value investing principles."""

from __future__ import annotations

from pathlib import Path

from moatlab.agents.base import BaseAgent
from moatlab.tools.portfolio import PORTFOLIO_DISPATCH, PORTFOLIO_TOOLS


_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "portfolio.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


class PortfolioAgent(BaseAgent):
    """Manages portfolio: record trades, track P&L, review holdings."""

    def __init__(self, model: str | None = None):
        super().__init__(
            name="PortfolioAgent",
            system_prompt=_load_prompt(),
            tools=PORTFOLIO_TOOLS,
            tool_dispatch=PORTFOLIO_DISPATCH,
            model=model,
        )

    def manage(self, action_description: str) -> str:
        """Execute a portfolio management action described in natural language."""
        return self.run(action_description)
