import app.db as db
def next_portfolio_id() -> int:
    db.next_portfolio_id += 1
    return db.next_portfolio_id - 1

def next_tx_id() -> int:
    db.next_tx_id += 1
    return db.next_tx_id - 1
