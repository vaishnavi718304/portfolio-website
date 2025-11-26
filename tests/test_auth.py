# tests/test_auth.py
from __future__ import annotations

import pytest

from app.services import auth
from app.domain.user import User


def test_login_admin_success(seed_data, monkeypatch, no_pause):
    # Simulate correct username/password input
    answers = iter(["admin", "admin123"])
    # Patch the ask() function *inside* auth
    monkeypatch.setattr(auth, "ask", lambda prompt: next(answers))

    user = auth.login()
    assert isinstance(user, User)
    assert user.username == "admin"
    assert user.role == "admin"


def test_login_user_wrong_password(seed_data, monkeypatch):
    # Correct username, wrong password
    answers = iter(["admin", "wrongpw"])
    monkeypatch.setattr(auth, "ask", lambda prompt: next(answers))

    with pytest.raises(ValueError):
        auth.login()


def test_login_unknown_user(monkeypatch):
    # Non-existent username
    answers = iter(["ghost", "pw"])
    monkeypatch.setattr(auth, "ask", lambda prompt: next(answers))

    with pytest.raises(ValueError):
        auth.login()


def test_is_admin(seed_data):
    admin = seed_data["admin"]
    user = seed_data["user"]

    assert auth.is_admin(admin) is True
    assert auth.is_admin(user) is False
    assert auth.is_admin(None) is False


def test_logout_returns_none(seed_data):
    admin = seed_data["admin"]
    assert auth.logout(admin) is None
