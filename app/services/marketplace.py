import time
import app.db as db
from app.utils.io import print_header, ask, pause
from app.utils.ids import next_tx_id
from app.services.portfolios import _portfolio_by_id, _owner_user, _ref_price

def list_securities(current_user):
    print_header("Securities")
    print(f"{'ticker':<6} {'name':<20} {'ref_price':>10}")
    for s in db.securities.values():
        print(f"{s['ticker']:<6} {s['name']:<20} {s['ref_price']:>10.2f}")
    pause()

def buy_security(current_user):
    print_header("Buy Security")
    try:
        pid = int(ask("Portfolio ID"))
        p = _portfolio_by_id(pid)
        owner = _owner_user(p["owner"])
        ticker = ask("Ticker").upper()
        price_mode = ask("Use reference price? (y/n)").lower()
        if price_mode not in {"y", "n"}:
            raise ValueError("Answer y or n.")
        price = _ref_price(ticker) if price_mode == "y" else float(ask("Price per unit"))
        if price < 0:
            raise ValueError("Price must be non-negative.")
        qty = float(ask("Quantity to buy"))
        if qty <= 0:
            raise ValueError("Quantity must be positive.")

        cost = price * qty
        cash = float(owner["balance"])
        if cost > cash:
            raise ValueError("Insufficient balance to complete purchase.")

        # deduct cash and add holdings
        owner["balance"] = cash - cost
        p["holdings"][ticker] = float(p["holdings"].get(ticker, 0.0)) + qty

        # audit
        db.transactions.append({
            "id": next_tx_id(), "ts": int(time.time()), "type": "BUY",
            "portfolio_id": pid, "ticker": ticker, "qty": qty, "price": price, "subtotal": cost
        })
        print("✅ Purchase recorded.")
    except ValueError:
        raise
    finally:
        pause()
