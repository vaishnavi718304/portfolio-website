# app/services/auth.py
from typing import Optional, Dict
import app.db as db
from app.utils.io import ask

def login(current_user: Optional[Dict] = None) -> Dict:
    username = ask("Username")
    password = ask("Password")
    user = db.users.get(username)
    if not user or user["password"] != password:
        raise ValueError("Login failed. Check username/password.")
    return user

def logout(current_user: Optional[Dict] = None) -> None:
    return None

def is_admin(current_user: Optional[Dict]) -> bool:
    return bool(current_user and current_user.get("role") == "admin")
