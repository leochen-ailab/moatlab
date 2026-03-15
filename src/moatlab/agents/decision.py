"""DecisionAgent — Final investment decision based on all analysis reports."""

from __future__ import annotations

from pathlib import Path

from moatlab.agents.base import BaseAgent


_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "decision.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


class DecisionAgent(BaseAgent):
    """Synthesizes all analysis reports into a Buy/Hold/Sell/Pass recommendation."""

    def __init__(self, model: str | None = None):
        super().__init__(
            name="DecisionAgent",
            system_prompt=_load_prompt(),
            tools=[],  # No tools — pure reasoning on provided reports
            tool_dispatch={},
            model=model,
        )

    def decide(self, ticker: str, reports: dict[str, str]) -> str:
        """Make investment decision based on collected analysis reports.

        Args:
            ticker: Stock ticker symbol.
            reports: Dict of agent_name -> analysis report text.
        """
        report_sections = []
        for agent_name, report in reports.items():
            report_sections.append(f"## {agent_name} 分析报告\n\n{report}")

        combined = f"请对 {ticker} 做出最终投资决策。以下是各 Agent 的分析报告：\n\n" + "\n\n---\n\n".join(report_sections)

        return self.run(combined)
