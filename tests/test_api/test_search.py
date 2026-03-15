"""测试股票搜索 API 端点。"""

import pytest
from fastapi.testclient import TestClient

from moatlab.server import app

client = TestClient(app)


class TestSearchAPI:
    """测试 /api/search/stocks 端点。"""

    def test_search_with_valid_ticker(self):
        """测试有效 ticker 搜索"""
        response = client.get("/api/search/stocks?q=AAPL")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "query" in data
        assert "total" in data
        assert data["query"] == "AAPL"
        assert len(data["results"]) > 0
        assert data["results"][0]["ticker"] == "AAPL"

    def test_search_with_chinese_name(self):
        """测试中文公司名搜索"""
        response = client.get("/api/search/stocks?q=苹果")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) > 0
        assert any(r["ticker"] == "AAPL" for r in data["results"])

    def test_search_with_english_name(self):
        """测试英文公司名搜索"""
        response = client.get("/api/search/stocks?q=apple")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) > 0
        assert any(r["ticker"] == "AAPL" for r in data["results"])

    def test_search_with_limit(self):
        """测试结果数量限制"""
        response = client.get("/api/search/stocks?q=a&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= 3

    def test_search_empty_query(self):
        """测试空查询"""
        response = client.get("/api/search/stocks?q=")
        assert response.status_code == 400

    def test_search_missing_query(self):
        """测试缺少查询参数"""
        response = client.get("/api/search/stocks")
        assert response.status_code == 422  # FastAPI validation error

    def test_search_invalid_limit_too_small(self):
        """测试 limit 过小"""
        response = client.get("/api/search/stocks?q=AAPL&limit=0")
        assert response.status_code == 400

    def test_search_invalid_limit_too_large(self):
        """测试 limit 过大"""
        response = client.get("/api/search/stocks?q=AAPL&limit=100")
        assert response.status_code == 400

    def test_search_result_structure(self):
        """测试返回结果结构"""
        response = client.get("/api/search/stocks?q=AAPL")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "query" in data
        assert "total" in data

        if len(data["results"]) > 0:
            result = data["results"][0]
            assert "ticker" in result
            assert "name" in result
            assert "name_cn" in result
            assert "sector" in result
            assert "match_score" in result

    def test_search_no_results(self):
        """测试无匹配结果"""
        response = client.get("/api/search/stocks?q=xyz123unknown")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["results"]) == 0

    def test_search_case_insensitive(self):
        """测试大小写不敏感"""
        response1 = client.get("/api/search/stocks?q=AAPL")
        response2 = client.get("/api/search/stocks?q=aapl")
        assert response1.status_code == 200
        assert response2.status_code == 200
        data1 = response1.json()
        data2 = response2.json()
        assert data1["results"][0]["ticker"] == data2["results"][0]["ticker"]

    @pytest.mark.parametrize("query,expected_ticker", [
        ("微软", "MSFT"),
        ("谷歌", "GOOGL"),
        ("特斯拉", "TSLA"),
    ])
    def test_search_company_mappings(self, query, expected_ticker):
        """测试公司名映射"""
        response = client.get(f"/api/search/stocks?q={query}")
        assert response.status_code == 200
        data = response.json()
        assert any(r["ticker"] == expected_ticker for r in data["results"])
