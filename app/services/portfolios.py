import time
import app.db as db
from app.utils.io import print_header, ask, pause
from app.utils.ids import next_portfolio_id, next_tx_id

def _ref_price(ticker: str) -> float:
    s = db.securities.get(ticker.upper())
    if not s:
        raise ValueError("Ticker not found.")
    return float(s["ref_price"])

def _portfolio_by_id(pid: int):
    for p in db.portfolios:
        if p["id"] == pid:
            return p
    raise ValueError("Portfolio not found.")

def _owner_user(username: str):
    u = db.users.get(username)
    if not u:
        raise ValueError("Owner must be an existing username.")
    return u

def _portfolio_total_value(p) -> float:
    total = 0.0
    for t, q in p["holdings"].items():
        total += float(q) * _ref_price(t)
    return total

def view_portfolios(current_user):
    print_header("Portfolios")
    if not db.portfolios:
        print("(none)")
        pause()
        return
    print(f"{'id':<4} {'owner':<12} {'name':<18} {'total_value':>12}  {'holdings'}")
    for p in db.portfolios:
        holdings = ", ".join(f"{t}:{q}" for t, q in p["holdings"].items()) or "-"
        print(f"{p['id']:<4} {p['owner']:<12} {p['name']:<18} { _portfolio_total_value(p):>12.2f}  {holdings}")
    pause()

def create_portfolio(current_user):
    print_header("Create Portfolio")
    owner = ask("Owner username")
    _owner_user(owner)
    name = ask("Portfolio name")
    desc = ask("Description")
    strat = ask("Strategy")
    pid = next_portfolio_id()
    db.portfolios.append({
        "id": pid, "owner": owner, "name": name,
        "description": desc, "strategy": strat, "holdings": {}
    })
    print(f"✅ Portfolio #{pid} created.")
    pause()

def sell_investment(current_user):
    print_header("Sell Investment")
    try:
        pid = int(ask("Portfolio ID"))
        p = _portfolio_by_id(pid)
        ticker = ask("Ticker").upper()
        if ticker not in p["holdings"]:
            raise ValueError("This portfolio does not hold that ticker.")
        qty = float(ask("Quantity to sell"))
        if qty <= 0:
            raise ValueError("Quantity must be positive.")
        held = float(p["holdings"].get(ticker, 0.0))
        if qty > held:
            raise ValueError("Insufficient position to sell that quantity.")
        price = float(ask("Sale price per unit"))
        if price < 0:
            raise ValueError("Price must be non-negative.")
        # update holdings
        new_qty = held - qty
        if new_qty == 0:
            del p["holdings"][ticker]
        else:
            p["holdings"][ticker] = new_qty
        # update cash
        owner = _owner_user(p["owner"])
        cash = float(owner["balance"])
        subtotal = price * qty
        owner["balance"] = cash + subtotal
        # audit
        db.transactions.append({
            "id": next_tx_id(), "ts": int(time.time()), "type": "SELL",
            "portfolio_id": pid, "ticker": ticker, "qty": qty, "price": price, "subtotal": subtotal
        })
        print("✅ Sale recorded.")
    except ValueError as e:
        raise
    finally:
        pause()
