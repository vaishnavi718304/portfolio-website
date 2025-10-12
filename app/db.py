from typing import Dict, List

# very simple in-memory store + seed data
users: Dict[str, Dict] = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin", "balance": 10_000.0},
    "alice": {"username": "alice", "password": "alice123", "role": "user", "balance": 5_000.0},
}

securities: Dict[str, Dict] = {
    "AAPL": {"ticker": "AAPL", "name": "Apple Inc.", "ref_price": 190.0},
    "MSFT": {"ticker": "MSFT", "name": "Microsoft", "ref_price": 420.0},
    "TSLA": {"ticker": "TSLA", "name": "Tesla", "ref_price": 200.0},
}

portfolios: List[Dict] = []  # each: {id, owner, name, description, strategy, holdings: {ticker: qty}}
transactions: List[Dict] = []  # simple audit list
next_portfolio_id = 1
