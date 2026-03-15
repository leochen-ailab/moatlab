"""测试股票搜索功能。"""

import pytest

from moatlab.tools.stock_search import is_valid_ticker, search_stocks


class TestIsValidTicker:
    """测试 ticker 格式验证。"""

    def test_valid_simple_ticker(self):
        """测试简单 ticker（1-5 个字母）"""
        assert is_valid_ticker("AAPL")
        assert is_valid_ticker("MSFT")
        assert is_valid_ticker("A")
        assert is_valid_ticker("GOOGL")

    def test_valid_ticker_with_dash(self):
        """测试带连字符的 ticker"""
        assert is_valid_ticker("BRK-B")

    def test_invalid_ticker_too_long(self):
        """测试过长的 ticker"""
        assert not is_valid_ticker("TOOLONG")

    def test_invalid_ticker_with_numbers(self):
        """测试包含数字的 ticker"""
        assert not is_valid_ticker("AAPL1")

    def test_invalid_ticker_empty(self):
        """测试空字符串"""
        assert not is_valid_ticker("")


class TestSearchStocks:
    """测试股票搜索功能。"""

    def test_empty_query(self):
        """测试空查询"""
        assert search_stocks("") == []
        assert search_stocks("   ") == []

    def test_exact_ticker_match(self):
        """测试精确 ticker 匹配"""
        results = search_stocks("AAPL")
        assert len(results) > 0
        assert results[0]["ticker"] == "AAPL"
        assert results[0]["match_score"] == 1.0

    def test_case_insensitive_ticker(self):
        """测试 ticker 大小写不敏感"""
        results = search_stocks("aapl")
        assert len(results) > 0
        assert results[0]["ticker"] == "AAPL"

    def test_ticker_with_dash(self):
        """测试带连字符的 ticker"""
        results = search_stocks("BRK-B")
        assert len(results) > 0
        assert results[0]["ticker"] == "BRK-B"

    def test_chinese_company_name(self):
        """测试中文公司名搜索"""
        results = search_stocks("苹果")
        assert len(results) > 0
        assert any(r["ticker"] == "AAPL" for r in results)

    def test_english_company_name(self):
        """测试英文公司名搜索"""
        results = search_stocks("apple")
        assert len(results) > 0
        assert any(r["ticker"] == "AAPL" for r in results)

    @pytest.mark.parametrize("query,expected_ticker", [
        ("微软", "MSFT"),
        ("谷歌", "GOOGL"),
        ("特斯拉", "TSLA"),
        ("microsoft", "MSFT"),
        ("google", "GOOGL"),
        ("tesla", "TSLA"),
    ])
    def test_company_name_mapping(self, query, expected_ticker):
        """测试公司名映射"""
        results = search_stocks(query)
        assert len(results) > 0
        assert any(r["ticker"] == expected_ticker for r in results)

    def test_partial_match(self):
        """测试部分匹配"""
        results = search_stocks("微")
        # 应该匹配"微软"
        assert any(r["ticker"] == "MSFT" for r in results)

    def test_result_limit(self):
        """测试结果数量限制"""
        results = search_stocks("a", limit=5)
        assert len(results) <= 5

    def test_result_contains_required_fields(self):
        """测试结果包含必需字段"""
        results = search_stocks("AAPL")
        assert len(results) > 0
        result = results[0]
        assert "ticker" in result
        assert "name" in result
        assert "name_cn" in result
        assert "sector" in result
        assert "match_score" in result

    def test_results_sorted_by_score(self):
        """测试结果按匹配分数排序"""
        results = search_stocks("a", limit=10)
        if len(results) > 1:
            scores = [r["match_score"] for r in results]
            assert scores == sorted(scores, reverse=True)

    def test_no_duplicate_tickers(self):
        """测试结果无重复 ticker"""
        results = search_stocks("apple")
        tickers = [r["ticker"] for r in results]
        assert len(tickers) == len(set(tickers))

    def test_unknown_query(self):
        """测试未知查询"""
        results = search_stocks("xyz123unknown")
        assert results == []
