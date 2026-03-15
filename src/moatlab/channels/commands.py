"""Shared command parsing for chat channels."""

from __future__ import annotations

import re
from dataclasses import dataclass

HELP_COMMANDS = {"help", "/help", "帮助"}
ANALYZE_PATTERN = re.compile(r"(?:分析|analyze)\s*([a-zA-Z]{1,10})", flags=re.IGNORECASE)
TICKER_ONLY_PATTERN = re.compile(r"([a-zA-Z]{1,10})")


@dataclass
class Command:
    """Parsed user command."""

    type: str
    ticker: str = ""


def parse_command(text: str) -> Command:
    """Parse command text into a normalized command object."""
    normalized = text.strip()

    if normalized.lower() in HELP_COMMANDS:
        return Command(type="help")

    analyze_match = ANALYZE_PATTERN.fullmatch(normalized)
    if analyze_match:
        return Command(type="analyze", ticker=analyze_match.group(1).upper())

    ticker_match = TICKER_ONLY_PATTERN.fullmatch(normalized)
    if ticker_match:
        return Command(type="analyze", ticker=ticker_match.group(1).upper())

    return Command(type="unknown")
