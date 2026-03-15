"""SQLite persistence layer for portfolio management."""

from __future__ import annotations

import sqlite3
import logging
from datetime import date
from pathlib import Path

from moatlab.config import settings

logger = logging.getLogger(__name__)

_CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('buy', 'sell')),
    shares REAL NOT NULL CHECK(shares > 0),
    price REAL NOT NULL CHECK(price > 0),
    date TEXT NOT NULL,
    notes TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS positions (
    ticker TEXT PRIMARY KEY,
    shares REAL NOT NULL DEFAULT 0,
    avg_cost REAL NOT NULL DEFAULT 0,
    total_cost REAL NOT NULL DEFAULT 0,
    first_buy_date TEXT NOT NULL,
    last_trade_date TEXT NOT NULL,
    notes TEXT DEFAULT ''
);
"""


def _get_db_path() -> Path:
    """Return the database file path, creating parent directory if needed."""
    db_path = Path(settings.db_path).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def _connect() -> sqlite3.Connection:
    """Open a connection to the portfolio database."""
    conn = sqlite3.connect(str(_get_db_path()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    with _connect() as conn:
        conn.executescript(_CREATE_TABLES_SQL)
    logger.info(f"数据库初始化完成: {_get_db_path()}")


def add_transaction(
    ticker: str,
    action: str,
    shares: float,
    price: float,
    trade_date: str | None = None,
    notes: str = "",
) -> dict:
    """Record a buy/sell transaction and update positions accordingly.

    Returns the updated position or a confirmation of full sell.
    """
    ticker = ticker.upper()
    trade_date = trade_date or date.today().isoformat()

    with _connect() as conn:
        # Insert transaction record
        conn.execute(
            "INSERT INTO transactions (ticker, action, shares, price, date, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (ticker, action, shares, price, trade_date, notes),
        )

        # Update position
        row = conn.execute("SELECT * FROM positions WHERE ticker = ?", (ticker,)).fetchone()

        if action == "buy":
            if row:
                old_shares = row["shares"]
                old_cost = row["total_cost"]
                new_shares = old_shares + shares
                new_cost = old_cost + shares * price
                new_avg = new_cost / new_shares
                conn.execute(
                    "UPDATE positions SET shares=?, avg_cost=?, total_cost=?, last_trade_date=?, notes=? WHERE ticker=?",
                    (new_shares, new_avg, new_cost, trade_date, notes or row["notes"], ticker),
                )
            else:
                total_cost = shares * price
                conn.execute(
                    "INSERT INTO positions (ticker, shares, avg_cost, total_cost, first_buy_date, last_trade_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (ticker, shares, price, total_cost, trade_date, trade_date, notes),
                )
        elif action == "sell":
            if not row or row["shares"] < shares:
                available = row["shares"] if row else 0
                raise ValueError(f"{ticker} 持仓不足: 当前 {available} 股，试图卖出 {shares} 股")
            new_shares = row["shares"] - shares
            if new_shares <= 0:
                conn.execute("DELETE FROM positions WHERE ticker = ?", (ticker,))
                return {"ticker": ticker, "action": "sold_all", "shares_sold": shares, "price": price}
            else:
                # avg_cost stays the same on partial sell
                new_cost = new_shares * row["avg_cost"]
                conn.execute(
                    "UPDATE positions SET shares=?, total_cost=?, last_trade_date=? WHERE ticker=?",
                    (new_shares, new_cost, trade_date, ticker),
                )

    return get_position(ticker) or {"ticker": ticker, "action": action, "shares": shares}


def get_positions() -> list[dict]:
    """Return all current positions."""
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM positions ORDER BY total_cost DESC").fetchall()
    return [dict(r) for r in rows]


def get_position(ticker: str) -> dict | None:
    """Return a single position by ticker."""
    ticker = ticker.upper()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM positions WHERE ticker = ?", (ticker,)).fetchone()
    return dict(row) if row else None


def get_transactions(ticker: str | None = None, limit: int = 50) -> list[dict]:
    """Return transaction history, optionally filtered by ticker."""
    with _connect() as conn:
        if ticker:
            rows = conn.execute(
                "SELECT * FROM transactions WHERE ticker = ? ORDER BY date DESC, id DESC LIMIT ?",
                (ticker.upper(), limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM transactions ORDER BY date DESC, id DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [dict(r) for r in rows]


def delete_position(ticker: str) -> bool:
    """Remove a position entirely (used for corrections)."""
    ticker = ticker.upper()
    with _connect() as conn:
        cursor = conn.execute("DELETE FROM positions WHERE ticker = ?", (ticker,))
    return cursor.rowcount > 0
