# app/db.py
"""
Legacy in-memory 'database' from Assignment 1.

For Assignment 2 we are migrating to SQLAlchemy + MySQL, but some
older CLI code may still import this module. To avoid crashes,
we keep a simple dict-based mock here.

New A2 features should NOT rely on this.
"""

from typing import Dict, List

# simple in-memory users (used only by old A1-style code)
users: Dict[str, Dict] = {
    "admin": {
        "username": "admin",
        "password": "admin123",
        "role": "admin",
        "first_name": "System",
        "last_name": "Admin",
        "balance": 10_000.0,
    },
    "alice": {
        "username": "alice",
        "password": "alice123",
        "role": "user",
        "first_name": "Alice",
        "last_name": "Lee",
        "balance": 5_000.0,
    },
}

# simple in-memory securities
securities: Dict[str, Dict] = {
    "AAPL": {"ticker": "AAPL", "name": "Apple Inc.", "ref_price": 190.0},
    "MSFT": {"ticker": "MSFT", "name": "Microsoft", "ref_price": 420.0},
    "TSLA": {"ticker": "TSLA", "name": "Tesla", "ref_price": 200.0},
}

# portfolios and transactions as simple lists of dicts
portfolios: List[Dict] = []       # {id, owner, name, description, strategy, holdings: {ticker: qty}}
transactions: List[Dict] = []     # {id, ts, type, portfolio_id, ticker, qty, price, subtotal}

next_portfolio_id: int = 1
next_tx_id: int = 1
