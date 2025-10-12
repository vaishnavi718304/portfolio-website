import app.db as db
from app.utils.io import print_header, ask, pause

def _next_id() -> int:
    db.next_portfolio_id += 1
    return db.next_portfolio_id - 1

def view_portfolios(current_user):
    print_header("Portfolios")
    if not db.portfolios:
        print("(none)")
        pause()
        return
    print(f"{'id':<4} {'owner':<10} {'name':<16} {'holdings':<20}")
    for p in db.portfolios:
        holdings = ", ".join(f"{t}:{q}" for t, q in p["holdings"].items()) or "-"
        print(f"{p['id']:<4} {p['owner']:<10} {p['name']:<16} {holdings:<20}")
    pause()

def create_portfolio(current_user):
    print_header("Create Portfolio")
    owner = ask("Owner username")
    if owner not in db.users:
        raise ValueError("Owner must be an existing username.")
    name = ask("Portfolio name")
    desc = ask("Description")
    strat = ask("Strategy")
    pid = _next_id()
    db.portfolios.append({
        "id": pid, "owner": owner, "name": name,
        "description": desc, "strategy": strat, "holdings": {}
    })
    print(f"✅ Portfolio #{pid} created.")
    pause()

def sell_investment(current_user):
    print_header("Sell Investment (stub)")
    print("For MVP, this is a stub. You can implement later.")
    pause()
