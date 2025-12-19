# tests/test_marketplace.py
from __future__ import annotations

import pytest

import app.database as database
from app.services import marketplace
from app.utils import io as io_mod
from app.domain.exceptions import ValidationError, AuthorizationError, NotFoundError
from app.domain.investment import Investment
from app.domain.transaction import Transaction
from app.domain.user import User


def test_list_securities_ok(seed_data, no_pause):
    user = seed_data["user"]
    marketplace.list_securities(user)  # should not raise


def test_buy_security_reference_price_success(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]
    p = seed_data["user_portfolio"]

    # Make sure user has plenty of cash AND that there is an AAPL holding row
    with database.get_session() as session:
        u = session.get(User, user.username)
        u.balance = 10_000.0  # lots of cash

        inv = (
            session.query(Investment)
            .filter_by(portfolio_id=p.id, security_ticker="AAPL")
            .first()
        )
        if inv is None:
            inv = Investment(
                portfolio_id=p.id,
                security_ticker="AAPL",
                quantity=0,
                avg_price=190.0,
            )
            session.add(inv)

        session.commit()
        start_balance = u.balance

    # portfolio id -> ticker -> use reference price -> quantity
    answers = iter([
        str(p.id),  # portfolio id
        "AAPL",     # ticker
        "y",        # use reference price
        "2",        # quantity
    ])
    # Patch the ask() used *inside* app.services.marketplace
    monkeypatch.setattr(marketplace, "ask", lambda prompt: next(answers))

    # act
    marketplace.buy_security(user)

    # assert
    with database.get_session() as session:
        u = session.get(User, user.username)

        inv = (
            session.query(Investment)
            .filter_by(portfolio_id=p.id, security_ticker="AAPL")
            .one()
        )

        tx = (
            session.query(Transaction)
            .filter_by(
                username=user.username,
                portfolio_id=p.id,
                security_ticker="AAPL",
                type="BUY",
            )
            .order_by(Transaction.id.desc())
            .first()
        )

        assert u.balance < start_balance
        assert inv.quantity >= 2
        assert tx is not None
        assert tx.quantity == 2
        assert tx.type == "BUY"


def test_buy_security_insufficient_balance(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]
    p = seed_data["user_portfolio"]

    # First, set a small balance
    with database.get_session() as session:
        u = session.get(User, user.username)
        u.balance = 10.0
        session.commit()

    # Try to buy 10 MSFT @ reference price 340 -> 3400 cost
    answers = iter([
        str(p.id),
        "MSFT",
        "y",
        "10",
    ])
    monkeypatch.setattr(marketplace, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        marketplace.buy_security(user)

def test_list_securities_requires_login(no_pause):
    # If no user is logged in, list_securities should fail fast
    with pytest.raises(AuthorizationError):
        marketplace.list_securities(None)

def test_buy_security_invalid_portfolio_id_format(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]

    # First answer is "abc" for Portfolio ID → int() fails → ValidationError
    answers = iter(["abc"])
    monkeypatch.setattr(marketplace, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        marketplace.buy_security(user)
def test_buy_security_portfolio_not_found(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]

    # 9999 is a valid integer but not an existing portfolio id → NotFoundError
    answers = iter(["9999", "AAPL", "y", "1"])
    monkeypatch.setattr(marketplace, "ask", lambda prompt: next(answers))

    with pytest.raises(NotFoundError):
        marketplace.buy_security(user)
def test_buy_security_unauthorized_portfolio(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]
    admin_portfolio = seed_data["admin_portfolio"]

    # User tries to buy into admin’s portfolio → AuthorizationError
    answers = iter([str(admin_portfolio.id), "AAPL", "y", "1"])
    monkeypatch.setattr(marketplace, "ask", lambda prompt: next(answers))

    with pytest.raises(AuthorizationError):
        marketplace.buy_security(user)
def test_buy_security_unknown_ticker(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]
    p = seed_data["user_portfolio"]

    # Ticker does not exist in the DB → _get_security raises ValidationError
    answers = iter([str(p.id), "ZZZZ", "y", "1"])
    monkeypatch.setattr(marketplace, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        marketplace.buy_security(user)
def test_buy_security_manual_price_invalid_number(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]
    p = seed_data["user_portfolio"]

    # price_mode = 'n' so function will ask for a manual price → 'abc' fails float()
    # Answers: [Portfolio ID, Ticker, Use ref price?, Quantity, Price per unit]
    answers = iter([str(p.id), "AAPL", "n", "2", "abc"])
    monkeypatch.setattr(marketplace, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        marketplace.buy_security(user)
def test_buy_security_negative_quantity(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]
    p = seed_data["user_portfolio"]

    # Quantity = -1 → passes int() but fails the "must be positive" check
    answers = iter([str(p.id), "AAPL", "y", "-1"])
    monkeypatch.setattr(marketplace, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        marketplace.buy_security(user)

def test_buy_security_empty_ticker_fails(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]
    p = seed_data["user_portfolio"]

    answers = iter([
        str(p.id),  # valid portfolio id
        "",         # empty ticker -> should fail before asking anything else
    ])
    monkeypatch.setattr(marketplace, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        marketplace.buy_security(user)


def test_buy_security_invalid_price_mode_fails(seed_data, monkeypatch, no_pause):
    user = seed_data["user"]
    p = seed_data["user_portfolio"]

    answers = iter([
        str(p.id),  # portfolio id
        "AAPL",     # ticker
        "maybe",    # invalid answer instead of 'y' or 'n'
    ])
    monkeypatch.setattr(marketplace, "ask", lambda prompt: next(answers))

    with pytest.raises(ValidationError):
        marketplace.buy_security(user)
def test_print_header_outputs_title(capsys):
    """print_header should actually print the title text somewhere."""
    io_mod.print_header("My Title")
    out = capsys.readouterr().out
    assert "My Title" in out


def test_ask_uses_input_and_strips(monkeypatch):
    """ask() should call input() and strip whitespace."""
    prompts = []

    def fake_input(prompt: str) -> str:
        prompts.append(prompt)
        return "  hello  "

    monkeypatch.setattr("builtins.input", fake_input)

    result = io_mod.ask("Your name")

    assert result == "hello"
    # make sure our fake input was actually called
    assert any("Your name" in p for p in prompts)
