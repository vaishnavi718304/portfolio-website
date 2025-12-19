# app/services/users.py
from __future__ import annotations

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_session
from app.utils.io import print_header, ask, pause
from app.domain.user import User
from app.domain.exceptions import (
    ValidationError,
    AuthorizationError,
    NotFoundError,
)


def _require_admin(current_user: Optional[User]) -> None:
    """Helper to enforce admin-only actions."""
    if current_user is None or current_user.role != "admin":
        raise AuthorizationError("Only admin can perform this action.")


def view_users(current_user: Optional[User]) -> None:
    """
    Admin-only: list all users from the database.
    """
    _require_admin(current_user)

    print_header("Users")

    with get_session() as session:
        users: List[User] = session.scalars(select(User)).all()

        print(f"{'username':<12} {'first':<12} {'last':<12} {'role':<8} {'balance':>10}")
        for u in users:
            print(
                f"{u.username:<12} {u.first_name:<12} {u.last_name:<12} "
                f"{u.role:<8} {u.balance:>10.2f}"
            )

    pause()


def create_user(current_user: Optional[User]) -> None:
    """
    Admin-only: create a new user in the database.
    """
    _require_admin(current_user)

    print_header("Create User")

    username = ask("New username")
    if not username:
        raise ValidationError("Username is required.")

    password = ask("Password")
    if not password:
        raise ValidationError("Password is required.")

    first = ask("First name")
    last = ask("Last name")
    role = ask("Role (admin/user)").lower()
    if role not in {"admin", "user"}:
        raise ValidationError("Role must be 'admin' or 'user'.")

    try:
        balance = float(ask("Starting balance"))
        if balance < 0:
            raise ValueError
    except ValueError:
        raise ValidationError("Balance must be a non-negative number.")

    with get_session() as session:
        try:
            # check if username already exists
            existing = session.get(User, username)
            if existing is not None:
                raise ValidationError("Username already exists.")

            new_user = User(
                username=username,
                password=password,
                role=role,
                first_name=first,
                last_name=last,
                balance=balance,
            )

            session.add(new_user)
            session.commit()
            print("✅ User created.")
        except (SQLAlchemyError, ValidationError):
            session.rollback()
            # re-raise as-is; router will handle and show message
            raise

    pause()


def delete_user(current_user: Optional[User]) -> None:
    """
    Admin-only: delete a user from the database, with the same rules as A1:
      - cannot delete yourself
      - cannot delete user that still has portfolios
      - cannot delete the last admin
    """
    _require_admin(current_user)

    print_header("Delete User")
    victim_username = ask("Username to delete")

    if victim_username == (current_user.username if current_user else None):
        raise ValidationError("You cannot delete yourself.")

    with get_session() as session:
        try:
            victim = session.get(User, victim_username)
            if victim is None:
                raise NotFoundError("User not found.")

            # requirement: do not allow deletion if user has portfolios
            from app.domain.portfolio import Portfolio  # local import avoids cycles

            has_portfolios = session.scalar(
                select(func.count()).select_from(Portfolio).where(
                    Portfolio.owner_username == victim_username
                )
            )
            if has_portfolios and has_portfolios > 0:
                raise ValidationError(
                    "User has existing portfolios. Please delete all portfolios first."
                )

            # don't delete last admin
            if victim.role == "admin":
                admin_count = session.scalar(
                    select(func.count()).select_from(User).where(User.role == "admin")
                )
                if admin_count is not None and admin_count <= 1:
                    raise ValidationError("Cannot delete the last admin user.")

            session.delete(victim)
            session.commit()
            print("✅ User deleted.")
        except (SQLAlchemyError, ValidationError, NotFoundError):
            session.rollback()
            raise

    pause()
