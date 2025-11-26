# app/services/transactions.py
from __future__ import annotations

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database import get_session
from app.utils.io import print_header, ask, pause
from app.domain.user import User
from app.domain.transaction import Transaction
from app.domain.exceptions import (
    AuthorizationError,
    ValidationError,
    NotFoundError,
)


# ---------- helpers ----------

def _require_logged_in(current_user: Optional[User]) -> User:
    if current_user is None:
        raise AuthorizationError("You must be logged in to view transactions.")
    return current_user


def _print_transactions(title: str, txs: List[Transaction]) -> None:
    print_header(title)

    if not txs:
        print("No transactions found.")
        pause()
        return

    print(
        f"{'id':<4} {'when':<16} {'type':<5} "
        f"{'port':<5} {'ticker':<8} {'qty':>8} "
        f"{'price':>10} {'subtotal':>12}"
    )

    for t in txs:
        when = t.occurred_at.strftime("%Y-%m-%d %H:%M")
        print(
            f"{t.id:<4} {when:<16} {t.type:<5} "
            f"{t.portfolio_id:<5} {t.security_ticker:<8} "
            f"{t.quantity:>8.2f} {t.price:>10.2f} {t.subtotal:>12.2f}"
        )

    pause()


# ---------- public functions wired from router ----------

def view_user_transactions(current_user: Optional[User]) -> None:
    """
    Show *all* transactions for the logged-in user.
    """
    current_user = _require_logged_in(current_user)

    with get_session() as session:
        stmt = (
            select(Transaction)
            .options(
                joinedload(Transaction.portfolio),
                joinedload(Transaction.security),
            )
            .where(Transaction.username == current_user.username)
            .order_by(Transaction.occurred_at)
        )
        txs = session.scalars(stmt).all()

    _print_transactions(f"Transactions for user {current_user.username}", txs)


def view_portfolio_transactions(current_user: Optional[User]) -> None:
    """
    Show transactions for a specific portfolio ID.

    Non-admin users can only see their own portfolios.
    """
    current_user = _require_logged_in(current_user)

    try:
        pid = int(ask("Portfolio ID"))
    except ValueError:
        raise ValidationError("Portfolio ID must be an integer.")

    with get_session() as session:
        # optional check that portfolio exists & is owned by user
        from app.domain.portfolio import Portfolio

        portfolio = session.get(Portfolio, pid)
        if portfolio is None:
            raise NotFoundError("Portfolio not found.")

        if current_user.role != "admin" and portfolio.owner_username != current_user.username:
            raise AuthorizationError("You can only view your own portfolios.")

        stmt = (
            select(Transaction)
            .where(Transaction.portfolio_id == pid)
            .order_by(Transaction.occurred_at)
        )
        txs = session.scalars(stmt).all()

    _print_transactions(f"Transactions for portfolio {pid}", txs)


def view_security_transactions(current_user: Optional[User]) -> None:
    """
    Show all transactions for a given ticker for the logged-in user.
    """
    current_user = _require_logged_in(current_user)

    ticker = ask("Ticker").upper()
    if not ticker:
        raise ValidationError("Ticker is required.")

    with get_session() as session:
        stmt = (
            select(Transaction)
            .where(
                Transaction.username == current_user.username,
                Transaction.security_ticker == ticker,
            )
            .order_by(Transaction.occurred_at)
        )
        txs = session.scalars(stmt).all()

    _print_transactions(
        f"Transactions for {current_user.username} in {ticker}", txs
    )
