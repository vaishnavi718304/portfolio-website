import app.db as db
from app.utils.io import print_header, ask, pause

def list_securities(current_user):
    print_header("Securities")
    print(f"{'ticker':<6} {'name':<20} {'ref_price':>10}")
    for s in db.securities.values():
        print(f"{s['ticker']:<6} {s['name']:<20} {s['ref_price']:>10.2f}")
    pause()

def buy_security(current_user):
    print_header("Buy Security (stub)")
    print("For MVP, this is a stub. You can implement later.")
    pause()
