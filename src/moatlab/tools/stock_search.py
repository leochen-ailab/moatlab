"""股票搜索工具 — 支持公司名、ticker 搜索。"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from functools import lru_cache

from moatlab.data.company_mappings import COMPANY_TO_TICKER, TICKER_INFO


def is_valid_ticker(text: str) -> bool:
    """判断是否为有效的 ticker 格式（1-5 个字母，可能包含 -）。"""
    return bool(re.match(r"^[A-Za-z]{1,5}(-[A-Za-z])?$", text))


def fuzzy_match_score(query: str, target: str) -> float:
    """计算模糊匹配分数（0-1）。

    使用 SequenceMatcher 计算字符串相似度。
    """
    return SequenceMatcher(None, query.lower(), target.lower()).ratio()


@lru_cache(maxsize=128)
def search_stocks(query: str, limit: int = 10) -> list[dict]:
    """搜索股票。

    支持：
    - 精确 ticker 匹配：AAPL
    - 公司名映射：苹果 → AAPL, apple → AAPL
    - 部分匹配：微 → 微软 (MSFT)
    - 模糊匹配：appl → AAPL, 苹果公司 → AAPL

    Args:
        query: 搜索关键词
        limit: 返回结果数量上限

    Returns:
        搜索结果列表，每项包含 ticker, name, name_cn, sector, match_score
    """
    if not query or not query.strip():
        return []

    query_lower = query.lower().strip()
    results = []
    seen_tickers = set()

    # 1. 精确 ticker 匹配
    if is_valid_ticker(query_lower):
        ticker = query.upper()
        if ticker in TICKER_INFO:
            info = TICKER_INFO[ticker]
            results.append({
                "ticker": ticker,
                "name": info["name"],
                "name_cn": info.get("name_cn", ""),
                "sector": info.get("sector", ""),
                "match_score": 1.0,
            })
            seen_tickers.add(ticker)

    # 2. 公司名精确匹配
    if query_lower in COMPANY_TO_TICKER:
        ticker = COMPANY_TO_TICKER[query_lower]
        if ticker not in seen_tickers and ticker in TICKER_INFO:
            info = TICKER_INFO[ticker]
            results.append({
                "ticker": ticker,
                "name": info["name"],
                "name_cn": info.get("name_cn", ""),
                "sector": info.get("sector", ""),
                "match_score": 1.0,
            })
            seen_tickers.add(ticker)

    # 3. 部分匹配（子串）
    for name, ticker in COMPANY_TO_TICKER.items():
        if ticker in seen_tickers:
            continue
        if query_lower in name:
            if ticker in TICKER_INFO:
                info = TICKER_INFO[ticker]
                # 计算匹配分数（查询词长度 / 公司名长度）
                score = len(query_lower) / len(name)
                results.append({
                    "ticker": ticker,
                    "name": info["name"],
                    "name_cn": info.get("name_cn", ""),
                    "sector": info.get("sector", ""),
                    "match_score": score,
                })
                seen_tickers.add(ticker)

    # 4. 模糊匹配（相似度 > 0.6）
    if len(results) < limit:
        fuzzy_candidates = []
        for name, ticker in COMPANY_TO_TICKER.items():
            if ticker in seen_tickers:
                continue
            score = fuzzy_match_score(query_lower, name)
            if score > 0.6:  # 相似度阈值
                fuzzy_candidates.append((ticker, score))

        # 按相似度排序
        fuzzy_candidates.sort(key=lambda x: x[1], reverse=True)

        for ticker, score in fuzzy_candidates[:limit - len(results)]:
            if ticker in TICKER_INFO:
                info = TICKER_INFO[ticker]
                results.append({
                    "ticker": ticker,
                    "name": info["name"],
                    "name_cn": info.get("name_cn", ""),
                    "sector": info.get("sector", ""),
                    "match_score": score * 0.9,  # 降权模糊匹配
                })
                seen_tickers.add(ticker)

    # 按匹配分数降序排序
    results.sort(key=lambda x: x["match_score"], reverse=True)

    return results[:limit]
