"""指令解析器：用户消息文本 → 结构化指令。

支持模糊匹配：
- 同义词触发：分析/研究/看看/analyze/research → analyze
- 公司名 → ticker 映射：苹果→AAPL、apple→AAPL、谷歌→GOOGL 等
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from moatlab.data.company_mappings import COMPANY_TO_TICKER

# ── 同义词映射 ─────────────────────────────────────────────────────

_ANALYZE_KEYWORDS = {
    "分析", "研究", "看看", "看下", "查一下", "查下", "帮我看看", "帮我分析",
    "analyze", "analyse", "research", "check", "look",
}

_HELP_KEYWORDS = {"帮助", "help", "/help", "使用说明", "怎么用"}


@dataclass
class Command:
    type: str  # "analyze" | "help" | "unknown"
    ticker: str = ""


def parse_command(text: str) -> Command:
    """解析用户消息为结构化指令。

    支持格式：
      - "分析 AAPL" / "研究 apple" / "看看 苹果"
      - "帮助" / "help"
      - 直接输入 ticker：如 "AAPL"
    """
    text = text.strip()
    if not text:
        return Command(type="unknown")

    # 帮助
    if text.lower() in _HELP_KEYWORDS or text.lower().rstrip("?？") in _HELP_KEYWORDS:
        return Command(type="help")

    # 尝试匹配 "<关键词> <目标>" 模式
    parts = re.split(r"\s+", text, maxsplit=1)
    if len(parts) == 2:
        keyword, target = parts[0], parts[1]
        if keyword.lower() in _ANALYZE_KEYWORDS:
            ticker = _resolve_ticker(target)
            if ticker:
                return Command(type="analyze", ticker=ticker)

    # 直接输入 ticker 或公司名（无前缀关键词）
    ticker = _resolve_ticker(text)
    if ticker:
        return Command(type="analyze", ticker=ticker)

    return Command(type="unknown")


def _resolve_ticker(target: str) -> str:
    """将用户输入解析为 ticker symbol。

    优先级：
    1. 公司名映射表匹配（优先，避免 apple→APPLE 而非 AAPL）
    2. 纯 ticker（1-5 个字母）→ 直接大写返回
    """
    target = target.strip()

    # 先查公司名映射表（忽略大小写）
    mapped = _COMPANY_TO_TICKER.get(target.lower(), "")
    if mapped:
        return mapped

    # 纯 ticker：1-5 个英文字母，可能包含 - (如 BRK-B)
    if re.match(r"^[A-Za-z]{1,5}(-[A-Za-z])?$", target):
        return target.upper()

    return ""
