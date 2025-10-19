from typing import Dict, Optional
import app.db as db
from app.utils.io import print_header, ask, pause

def view_users(current_user: Optional[Dict]) -> None:
    print_header("Users")
    print(f"{'username':<12} {'first':<12} {'last':<12} {'role':<8} {'balance':>10}")
    for u in db.users.values():
        print(f"{u['username']:<12} {u.get('first_name',''):<12} {u.get('last_name',''):<12} "
              f"{u['role']:<8} {u['balance']:>10.2f}")
    pause()

def create_user(current_user: Optional[Dict]) -> None:
    print_header("Create User")
    username = ask("New username")
    if not username:
        raise ValueError("Username is required.")
    if username in db.users:
        raise ValueError("Username already exists.")
    password = ask("Password")
    if not password:
        raise ValueError("Password is required.")
    first = ask("First name")
    last = ask("Last name")
    role = ask("Role (admin/user)").lower()
    if role not in {"admin", "user"}:
        raise ValueError("Role must be 'admin' or 'user'.")
    try:
        balance = float(ask("Starting balance"))
        if balance < 0:
            raise ValueError
    except ValueError:
        raise ValueError("Balance must be a non-negative number.")
    db.users[username] = {
        "username": username, "password": password, "role": role,
        "first_name": first, "last_name": last, "balance": balance
    }
    print("✅ User created.")
    pause()

def delete_user(current_user: Optional[Dict]) -> None:
    print_header("Delete User")
    victim = ask("Username to delete")
    if victim == (current_user or {}).get("username"):
        raise ValueError("You cannot delete yourself.")
    if victim not in db.users:
        raise ValueError("User not found.")
    admins = sum(1 for u in db.users.values() if u["role"] == "admin")
    if db.users[victim]["role"] == "admin" and admins <= 1:
        raise ValueError("Cannot delete the last admin.")
    del db.users[victim]
    print("✅ User deleted.")
    pause()
