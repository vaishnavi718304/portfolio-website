# tests/test_transactions.py
from __future__ import annotations

import pytest

import app.database as database
from app.services import transactions as tx_service
from app.domain.transaction import Transaction
from app.domain.exceptions import ValidationError, AuthorizationError, NotFoundError



def _seed_one_transaction(seed_data):
    """Helper: ensure at least one transaction exists for user/portfolio/ticker."""
    user = seed_data["user"]
    p = seed_data["user_portfolio"]

    with database.get_session() as session:
        tx = Transaction(
            type="BUY",
            username=user.username,
            portfolio_id=p.id,
            investment_id=None,
            security_ticker="AAPL",
            quantity=1,
            price=190.0,
            subtotal=190.0,
        )
        session.add(tx)
        session.commit()


def test_view_user_transactions_ok(seed_data, no_pause):
    # seed at least one tx
    _seed_one_transaction(seed_data)
    user = seed_data["user"]

    # no input needed here, just make sure it runs
    tx_service.view_user_transactions(user)  # should not raise


def test_view_user_transactions_requires_login():
    # current_user = None → should raise AuthorizationError
    with pytest.raises(AuthorizationError):
        tx_service.view_user_transactions(None)


def test_view_portfolio_transactions_owner_ok(seed_data, no_pause, monkeypatch):
    _seed_one_transaction(seed_data)
    user = seed_data["user"]
    p = seed_data["user_portfolio"]

    answers = iter([str(p.id)])
    # Patch ask() in the transactions service module
    monkeypatch.setattr(tx_service, "ask", lambda prompt: next(answers))

    tx_service.view_portfolio_transactions(user)  # should not raise


def test_view_portfolio_transactions_not_found(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]

    answers = iter(["9999"])  # non-existent portfolio id
    monkeypatch.setattr(tx_service, "ask", lambda prompt: next(answers))

    with pytest.raises(NotFoundError):
        tx_service.view_portfolio_transactions(user)


def test_view_security_transactions_ok(seed_data, no_pause, monkeypatch):
    _seed_one_transaction(seed_data)
    user = seed_data["user"]

    answers = iter(["AAPL"])
    monkeypatch.setattr(tx_service, "ask", lambda prompt: next(answers))

    tx_service.view_security_transactions(user)  # should not raise
