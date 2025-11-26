# tests/test_portfolios.py
from __future__ import annotations

import pytest

import app.database as database
from app.services import portfolios
from app.domain.investment import Investment
from app.domain.transaction import Transaction
from app.domain.exceptions import (
    ValidationError,
    AuthorizationError,
    PortfolioNotEmptyError,
    NotFoundError,
)
from app.domain.user import User


def _ensure_aapl_investment(portfolio):
    """
    Helper: make sure there is an AAPL position in this portfolio.
    seed_data *should* already do this, but we enforce it here so the tests
    are not fragile.
    """
    with database.get_session() as session:
        inv = (
            session.query(Investment)
            .filter_by(portfolio_id=portfolio.id, security_ticker="AAPL")
            .one_or_none()
        )
        if inv is None:
            inv = Investment(
                portfolio_id=portfolio.id,
                security_ticker="AAPL",
                quantity=5,
                avg_price=190.0,
            )
            session.add(inv)
            session.commit()
    return inv


def test_create_portfolio_success(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]

    answers = iter(["NewPort", "My test portfolio"])
    # Patch the ask() used inside app.services.portfolios
    monkeypatch.setattr(portfolios, "ask", lambda prompt: next(answers))

    portfolios.create_portfolio(user)

    with database.get_session() as session:
        PortModel = type(seed_data["user_portfolio"])
        ports = (
            session.query(PortModel)
            .filter_by(owner_username=user.username, name="NewPort")
            .all()
        )
        assert len(ports) == 1


def test_delete_portfolio_with_investments_fails(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]
    p = seed_data["user_portfolio"]  # has an AAPL investment from seed_data

    answers = iter([str(p.id)])
    monkeypatch.setattr(portfolios, "ask", lambda prompt: next(answers))

    with pytest.raises(PortfolioNotEmptyError):
        portfolios.delete_portfolio(user)


def test_delete_portfolio_not_found(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]

    answers = iter(["9999"])
    monkeypatch.setattr(portfolios, "ask", lambda prompt: next(answers))

    with pytest.raises(NotFoundError):
        portfolios.delete_portfolio(user)


def test_harvest_investment_partial_sell_success(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]
    p = seed_data["user_portfolio"]

    # Ensure there's an AAPL holding to sell from.
    _ensure_aapl_investment(p)

    # Sell 2 out of existing AAPL at price 200
    answers = iter([
        str(p.id),  # portfolio ID
        "AAPL",     # ticker
        "2",        # quantity to sell
        "200",      # sale price
    ])
    monkeypatch.setattr(portfolios, "ask", lambda prompt: next(answers))

    # Before: capture quantity and balance
    with database.get_session() as session:
        inv_before = (
            session.query(Investment)
            .filter_by(portfolio_id=p.id, security_ticker="AAPL")
            .one()
        )
        start_qty = inv_before.quantity
        start_balance = session.get(User, user.username).balance

    # act
    portfolios.harvest_investment(user)

    # After: check that quantity dropped by 2, balance increased, and SELL tx logged
    with database.get_session() as session:
        inv_after = (
            session.query(Investment)
            .filter_by(portfolio_id=p.id, security_ticker="AAPL")
            .one()
        )
        u = session.get(User, user.username)

        tx = (
            session.query(Transaction)
            .filter_by(
                username=user.username,
                portfolio_id=p.id,
                security_ticker="AAPL",
                type="SELL",
            )
            .order_by(Transaction.id.desc())
            .first()
        )

        assert inv_after.quantity == start_qty - 2
        assert u.balance == start_balance + 2 * 200
        assert tx is not None
        assert tx.quantity == 2
        assert tx.price == 200.0
        assert tx.type == "SELL"


def test_harvest_investment_too_much_fails(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]
    p = seed_data["user_portfolio"]

    # make sure there *is* some AAPL, then try to oversell
    _ensure_aapl_investment(p)

    answers = iter([
        str(p.id),
        "AAPL",
        "999",  # more than we own
        "200",
    ])
    monkeypatch.setattr(portfolios, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        portfolios.harvest_investment(user)
def test_investment_alias_properties_and_str():
    inv = Investment(
        portfolio_id=1,
        security_ticker="AAPL",
        quantity=5,
        avg_price=100.0,
    )

    # alias getters
    assert inv.ticker == "AAPL"
    assert inv.purchase_price == 100.0

    # alias setters should update underlying fields
    inv.ticker = "MSFT"
    inv.purchase_price = 200.0

    assert inv.security_ticker == "MSFT"
    assert inv.avg_price == 200.0

    # __str__ should include key info
    s = str(inv)
    assert "MSFT" in s
    assert "portfolio_id=1" in s
