"""Tests for portfolio tool functions."""

import os
import tempfile

import pytest

from moatlab.store.database import init_db
from moatlab.tools.portfolio import (
    add_position,
    get_portfolio,
    get_portfolio_performance,
    get_transaction_history,
    sell_position,
)


@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    """Use a temporary database for each test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    monkeypatch.setattr("moatlab.config.settings.db_path", db_path)
    init_db()
    yield db_path
    os.unlink(db_path)


class TestAddPosition:
    def test_success(self):
        result = add_position("AAPL", 100, 150.0, "2025-01-15", "建仓")
        assert result["status"] == "success"
        assert result["action"] == "buy"
        assert result["position"]["ticker"] == "AAPL"


class TestSellPosition:
    def test_success(self):
        add_position("AAPL", 100, 150.0, "2025-01-15")
        result = sell_position("AAPL", 50, 170.0, "2025-02-01")
        assert result["status"] == "success"

    def test_oversell_returns_error(self):
        add_position("AAPL", 10, 150.0, "2025-01-15")
        result = sell_position("AAPL", 100, 170.0, "2025-02-01")
        assert result["status"] == "error"
        assert "持仓不足" in result["message"]


class TestGetPortfolio:
    def test_empty(self):
        result = get_portfolio()
        assert result["position_count"] == 0
        assert result["positions"] == []

    def test_with_positions(self, monkeypatch):
        # Mock yfinance to avoid network calls
        class MockInfo:
            info = {"currentPrice": 200.0}

        monkeypatch.setattr("moatlab.tools.portfolio.yf.Ticker", lambda t: MockInfo())

        add_position("AAPL", 100, 150.0, "2025-01-15")
        result = get_portfolio()
        assert result["position_count"] == 1
        pos = result["positions"][0]
        assert pos["current_price"] == 200.0
        assert pos["market_value"] == 20000.0
        assert pos["pnl"] == 5000.0


class TestGetTransactionHistory:
    def test_empty(self):
        result = get_transaction_history()
        assert result["count"] == 0

    def test_with_records(self):
        add_position("AAPL", 100, 150.0, "2025-01-15")
        sell_position("AAPL", 30, 170.0, "2025-02-01")
        result = get_transaction_history()
        assert result["count"] == 2


class TestGetPerformance:
    def test_empty(self):
        result = get_portfolio_performance()
        assert "message" in result

    def test_with_data(self, monkeypatch):
        class MockInfo:
            info = {"currentPrice": 200.0}

        monkeypatch.setattr("moatlab.tools.portfolio.yf.Ticker", lambda t: MockInfo())

        add_position("AAPL", 100, 150.0, "2025-01-15")
        result = get_portfolio_performance()
        assert result["total_return"] > 0
        assert len(result["winners"]) == 1
