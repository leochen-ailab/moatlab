"""结果格式化：分析报告 → Lark 消息文本。"""

from __future__ import annotations


def format_analysis(ticker: str, reports: dict[str, str]) -> str:
    """将 Orchestrator 分析结果格式化为 Lark 消息文本。"""
    sections = [
        ("投资决策", reports.get("decision", "")),
        ("护城河分析", reports.get("moat", "")),
        ("管理层分析", reports.get("management", "")),
        ("财务分析", reports.get("financial", "")),
        ("估值分析", reports.get("valuation", "")),
    ]

    lines = [f"📊 {ticker} 价值投资分析\n"]
    for title, content in sections:
        if not content:
            continue
        lines.append(f"━━ {title} ━━")
        lines.append(_truncate(content, max_chars=4000))
        lines.append("")

    return "\n".join(lines)


def format_error(ticker: str, error: str) -> str:
    """格式化分析失败消息。"""
    return f"❌ 分析 {ticker} 失败：{error}"


def format_help() -> str:
    """返回帮助文本。"""
    return (
        "🏰 MoatLab — 价值投资分析 Bot\n"
        "\n"
        "📌 使用方式：\n"
        "  分析 AAPL — 全面分析苹果公司\n"
        "  研究 TSLA — 同上（支持同义词）\n"
        "  看看 谷歌 — 支持中文公司名\n"
        "  MSFT — 直接输入 ticker 也行\n"
        "\n"
        "💡 私聊直接发送，群聊需要 @我"
    )


def _truncate(text: str, max_chars: int = 4000) -> str:
    """截断过长文本。"""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n... (内容过长已截断)"
