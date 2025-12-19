# tests/test_users.py
from __future__ import annotations

import pytest

import app.database as database
from app.services import users
from app.domain.user import User
from app.domain.portfolio import Portfolio
from app.domain.exceptions import AuthorizationError, ValidationError, NotFoundError


def test_view_users_admin_ok(seed_data, no_pause):
    admin = seed_data["admin"]
    # just call; if it raises, test fails
    users.view_users(admin)


def test_view_users_non_admin_forbidden(seed_data):
    user = seed_data["user"]
    with pytest.raises(AuthorizationError):
        users.view_users(user)


def test_create_user_success(seed_data, monkeypatch, no_pause):
    admin = seed_data["admin"]

    # Pick a username that definitely does NOT exist yet in this DB.
    with database.get_session() as session:
        existing = {u.username for u in session.query(User).all()}

    base = "testuser"
    new_username = base
    i = 1
    while new_username in existing:
        new_username = f"{base}{i}"
        i += 1

    answers = iter([
        new_username,  # username (unique)
        "pw123",       # password
        "Test",        # first name
        "User",        # last name
        "user",        # role
        "1000",        # balance
    ])
    # Patch ask() in the users service module
    monkeypatch.setattr(users, "ask", lambda prompt: next(answers))

    users.create_user(admin)

    with database.get_session() as session:
        created = session.get(User, new_username)
        assert created is not None
        assert created.role == "user"
        assert created.balance == 1000.0


def test_create_user_duplicate_username(seed_data, monkeypatch, no_pause):
    admin = seed_data["admin"]

    answers = iter([
        "vaishnavi",     # already exists (from seed_data)
        "pw",
        "X",
        "Y",
        "user",
        "500",
    ])
    monkeypatch.setattr(users, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        users.create_user(admin)


def test_delete_user_with_portfolios_fails(seed_data, monkeypatch, no_pause):
    admin = seed_data["admin"]
    user = seed_data["user"]

    # user has a portfolio from seed_data
    answers = iter([user.username])
    monkeypatch.setattr(users, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        users.delete_user(admin)


def test_delete_user_not_found(seed_data, monkeypatch, no_pause):
    admin = seed_data["admin"]

    answers = iter(["ghost"])
    monkeypatch.setattr(users, "ask", lambda prompt: next(answers))

    with pytest.raises(NotFoundError):
        users.delete_user(admin)


def test_delete_user_cannot_delete_self(seed_data, monkeypatch, no_pause):
    admin = seed_data["admin"]
    answers = iter([admin.username])
    monkeypatch.setattr(users, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        users.delete_user(admin)
def test_create_user_invalid_role_fails(seed_data, monkeypatch, no_pause):
    admin = seed_data["admin"]

    answers = iter([
        "roleuser1",  # new username (won't exist yet)
        "pw123",
        "Test",
        "User",
        "manager",    # invalid role
        "500",
    ])
    monkeypatch.setattr(users, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        users.create_user(admin)


def test_create_user_negative_balance_fails(seed_data, monkeypatch, no_pause):
    admin = seed_data["admin"]

    answers = iter([
        "neguser1",
        "pw123",
        "Test",
        "User",
        "user",
        "-100",       # negative balance
    ])
    monkeypatch.setattr(users, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        users.create_user(admin)


def test_create_user_blank_username_fails(seed_data, monkeypatch, no_pause):
    admin = seed_data["admin"]

    answers = iter([
        "",           # blank username
        "pw123",
        "Test",
        "User",
        "user",
        "100",
    ])
    monkeypatch.setattr(users, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        users.create_user(admin)
