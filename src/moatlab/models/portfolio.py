"""Data models for portfolio management."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class TransactionAction(str, Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass
class Transaction:
    """A single buy/sell transaction."""

    id: int | None
    ticker: str
    action: TransactionAction
    shares: float
    price: float
    date: str  # ISO format YYYY-MM-DD
    notes: str = ""


@dataclass
class Position:
    """A current holding in the portfolio."""

    ticker: str
    shares: float
    avg_cost: float
    total_cost: float
    first_buy_date: str
    last_trade_date: str
    notes: str = ""


@dataclass
class PortfolioSummary:
    """Aggregated portfolio view with real-time data."""

    positions: list[dict] = field(default_factory=list)
    total_cost: float = 0.0
    total_market_value: float = 0.0
    total_return: float = 0.0
    total_return_pct: float = 0.0
    position_count: int = 0
