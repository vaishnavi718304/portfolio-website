# app/services/auth.py
from __future__ import annotations

from typing import Optional

from app.database import get_session
from app.domain.user import User
from app.utils.io import ask


def login(current_user: Optional[User] = None) -> User:
    """
    Authenticate a user using the database.

    - Prompts for username and password via console.
    - Looks up the User in the DB.
    - Raises ValueError if not found or password mismatch.
    - Returns the User ORM object on success.
    """
    username = ask("Username")
    password = ask("Password")

    with get_session() as session:
        user = session.get(User, username)

        if user is None or user.password != password:
            # keep the error message similar to your A1 behavior
            raise ValueError("Login failed. Check username/password.")

        return user


def logout(current_user: Optional[User] = None) -> None:
    """
    Clear the current logged-in user.

    The main loop in app/main.py will set current_user = None when this
    returns None, so we just return None explicitly.
    """
    return None


def is_admin(current_user: Optional[User]) -> bool:
    """
    Check if the current user is an admin.

    current_user is now a User ORM instance, not a dict.
    """
    return bool(current_user and current_user.role == "admin")
