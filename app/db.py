
from typing import Dict, List

users: Dict[str, Dict] = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin",
              "first_name": "System", "last_name": "Admin", "balance": 10_000.0},
    "alice": {"username": "alice", "password": "alice123", "role": "user",
              "first_name": "Alice", "last_name": "Lee", "balance": 5_000.0},
}

securities: Dict[str, Dict] = {
    "AAPL": {"ticker": "AAPL", "name": "Apple Inc.", "ref_price": 190.0},
    "MSFT": {"ticker": "MSFT", "name": "Microsoft", "ref_price": 420.0},
    "TSLA": {"ticker": "TSLA", "name": "Tesla", "ref_price": 200.0},
}

portfolios: List[Dict] = []       # {id, owner, name, description, strategy, holdings: {ticker: qty}}
transactions: List[Dict] = []     # {id, ts, type, portfolio_id, ticker, qty, price, subtotal}
next_portfolio_id = 1
next_tx_id = 1
