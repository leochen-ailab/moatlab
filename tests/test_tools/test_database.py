"""Tests for portfolio database CRUD operations."""

import os
import tempfile

import pytest

from moatlab.store.database import (
    add_transaction,
    delete_position,
    get_position,
    get_positions,
    get_transactions,
    init_db,
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


class TestAddTransaction:
    def test_buy_creates_position(self):
        result = add_transaction("AAPL", "buy", 100, 150.0, "2025-01-15")
        assert result["ticker"] == "AAPL"
        assert result["shares"] == 100.0
        assert result["avg_cost"] == 150.0

    def test_buy_updates_avg_cost(self):
        add_transaction("AAPL", "buy", 100, 150.0, "2025-01-15")
        result = add_transaction("AAPL", "buy", 50, 180.0, "2025-02-01")
        assert result["shares"] == 150.0
        expected_avg = (100 * 150 + 50 * 180) / 150
        assert abs(result["avg_cost"] - expected_avg) < 0.01

    def test_sell_reduces_shares(self):
        add_transaction("AAPL", "buy", 100, 150.0, "2025-01-15")
        result = add_transaction("AAPL", "sell", 30, 170.0, "2025-02-01")
        assert result["shares"] == 70.0
        assert result["avg_cost"] == 150.0  # avg_cost unchanged on sell

    def test_sell_all_removes_position(self):
        add_transaction("AAPL", "buy", 100, 150.0, "2025-01-15")
        result = add_transaction("AAPL", "sell", 100, 170.0, "2025-02-01")
        assert result["action"] == "sold_all"
        assert get_position("AAPL") is None

    def test_sell_too_many_raises(self):
        add_transaction("AAPL", "buy", 50, 150.0, "2025-01-15")
        with pytest.raises(ValueError, match="持仓不足"):
            add_transaction("AAPL", "sell", 100, 170.0, "2025-02-01")

    def test_sell_nonexistent_raises(self):
        with pytest.raises(ValueError, match="持仓不足"):
            add_transaction("AAPL", "sell", 10, 170.0, "2025-02-01")


class TestGetPositions:
    def test_empty_portfolio(self):
        assert get_positions() == []

    def test_multiple_positions(self):
        add_transaction("AAPL", "buy", 100, 150.0, "2025-01-15")
        add_transaction("MSFT", "buy", 50, 400.0, "2025-01-15")
        positions = get_positions()
        assert len(positions) == 2
        tickers = {p["ticker"] for p in positions}
        assert tickers == {"AAPL", "MSFT"}


class TestGetTransactions:
    def test_transaction_history(self):
        add_transaction("AAPL", "buy", 100, 150.0, "2025-01-15")
        add_transaction("AAPL", "sell", 30, 170.0, "2025-02-01")
        txns = get_transactions()
        assert len(txns) == 2

    def test_filter_by_ticker(self):
        add_transaction("AAPL", "buy", 100, 150.0, "2025-01-15")
        add_transaction("MSFT", "buy", 50, 400.0, "2025-01-15")
        txns = get_transactions("AAPL")
        assert len(txns) == 1
        assert txns[0]["ticker"] == "AAPL"


class TestDeletePosition:
    def test_delete_existing(self):
        add_transaction("AAPL", "buy", 100, 150.0, "2025-01-15")
        assert delete_position("AAPL") is True
        assert get_position("AAPL") is None

    def test_delete_nonexistent(self):
        assert delete_position("AAPL") is False
