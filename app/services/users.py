from typing import Dict
import app.db as db
from app.utils.io import print_header, ask, pause

def view_users(current_user: Dict | None) -> None:
    print_header("Users")
    print(f"{'username':<12} {'role':<8} {'balance':>10}")
    for u in db.users.values():
        print(f"{u['username']:<12} {u['role']:<8} {u['balance']:>10.2f}")
    pause()

def create_user(current_user: Dict | None) -> None:
    print_header("Create User")
    username = ask("New username")
    if username in db.users:
        raise ValueError("Username already exists.")
    password = ask("Password")
    role = ask("Role (admin/user)").lower()
    if role not in {"admin", "user"}:
        raise ValueError("Role must be 'admin' or 'user'.")
    try:
        balance = float(ask("Starting balance"))
        if balance < 0:
            raise ValueError
    except ValueError:
        raise ValueError("Balance must be a non-negative number.")
    db.users[username] = {"username": username, "password": password, "role": role, "balance": balance}
    print("✅ User created.")
    pause()

def delete_user(current_user: Dict | None) -> None:
    print_header("Delete User")
    victim = ask("Username to delete")
    if victim == current_user.get("username"):
        raise ValueError("You cannot delete yourself.")
    if victim not in db.users:
        raise ValueError("User not found.")
    # prevent deleting last admin
    admins = sum(1 for u in db.users.values() if u["role"] == "admin")
    if db.users[victim]["role"] == "admin" and admins <= 1:
        raise ValueError("Cannot delete the last admin.")
    del db.users[victim]
    print("✅ User deleted.")
    pause()
