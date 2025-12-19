# app/services/user_service.py
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.domain.user import User
from app.domain.portfolio import Portfolio
from app.domain.exceptions import ValidationError, NotFoundError


def get_all_users() -> List[User]:
    return db.session.scalars(select(User)).all()


def get_user_by_username(username: str) -> User:
    user = db.session.get(User, username)
    if user is None:
        raise NotFoundError("User not found.")
    return user


def create_user(
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    role: str = "user",
    balance: float = 0.0,
) -> User:
    if not username:
        raise ValidationError("Username is required.")
    if not password:
        raise ValidationError("Password is required.")
    if not first_name:
        raise ValidationError("First name is required.")
    if not last_name:
        raise ValidationError("Last name is required.")
    if role not in {"admin", "user"}:
        raise ValidationError("Role must be 'admin' or 'user'.")
    if balance < 0:
        raise ValidationError("Balance must be a non-negative number.")

    existing = db.session.get(User, username)
    if existing is not None:
        raise ValidationError("Username already exists.")

    user = User(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=role,
        balance=balance,
    )

    try:
        db.session.add(user)
        db.session.commit()
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValidationError(f"Database error while creating user: {e}")


def delete_user(username: str, requesting_username: Optional[str] = None) -> None:
    if requesting_username is not None and requesting_username == username:
        raise ValidationError("You cannot delete yourself.")

    user = db.session.get(User, username)
    if user is None:
        raise NotFoundError("User not found.")

    # Don't delete if user has portfolios
    has_portfolios = db.session.scalar(
        select(func.count()).select_from(Portfolio).where(Portfolio.owner_username == username)
    )
    if has_portfolios and has_portfolios > 0:
        raise ValidationError("User has existing portfolios. Delete portfolios first.")

    # Don't delete last admin
    if user.role == "admin":
        admin_count = db.session.scalar(
            select(func.count()).select_from(User).where(User.role == "admin")
        )
        if admin_count is not None and admin_count <= 1:
            raise ValidationError("Cannot delete the last admin user.")

    try:
        db.session.delete(user)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValidationError(f"Database error while deleting user: {e}")
