"""Format analysis reports for chat channels."""

from __future__ import annotations


def truncate(text: str, max_chars: int = 800) -> str:
    """Truncate long text blocks for chat readability."""
    cleaned = text.strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return f"{cleaned[:max_chars]}\n...(内容过长，已截断)"


def format_analysis(ticker: str, reports: dict[str, str], max_chars_per_section: int = 800) -> str:
    """Format orchestrator reports into a single Lark text message."""
    sections = [
        ("投资决策", reports.get("decision", "")),
        ("护城河分析", reports.get("moat", "")),
        ("管理层分析", reports.get("management", "")),
        ("财务分析", reports.get("financial", "")),
        ("估值分析", reports.get("valuation", "")),
    ]

    lines: list[str] = [f"📊 {ticker} 价值投资分析", ""]
    for title, content in sections:
        lines.append(f"━━ {title} ━━")
        lines.append(truncate(content or "暂无数据", max_chars=max_chars_per_section))
        lines.append("")

    return "\n".join(lines).strip()
