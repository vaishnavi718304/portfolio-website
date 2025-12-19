# app/services/marketplace.py
from __future__ import annotations

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_session
from app.utils.io import print_header, ask, pause
from app.domain.user import User
from app.domain.portfolio import Portfolio
from app.domain.security import Security
from app.domain.investment import Investment
from app.domain.transaction import Transaction
from app.domain.exceptions import (
    ValidationError,
    AuthorizationError,
    NotFoundError,
)


def _require_login(current_user: Optional[User]) -> None:
    if current_user is None:
        raise AuthorizationError("You must be logged in to use the marketplace.")


def _get_portfolio(session, pid: int) -> Portfolio:
    portfolio = session.get(Portfolio, pid)
    if portfolio is None:
        raise NotFoundError("Portfolio not found.")
    return portfolio


def _get_security(session, ticker: str) -> Security:
    sec = session.get(Security, ticker.upper())
    if sec is None:
        raise ValidationError(
            "Invalid ticker. Use 'View Securities' to see valid options."
        )
    return sec


def list_securities(current_user: Optional[User]) -> None:
    """Show all available securities from the DB."""
    _require_login(current_user)
    print_header("Securities")

    with get_session() as session:
        securities: List[Security] = session.scalars(select(Security)).all()

        print(f"{'ticker':<6} {'issuer':<20} {'price':>10}")
        for s in securities:
            print(f"{s.ticker:<6} {s.issuer:<20} {s.price:>10.2f}")

    pause()


def buy_security(current_user: Optional[User]) -> None:
    """Place a BUY order, update balances/holdings, and record a Transaction."""
    _require_login(current_user)
    print_header("Place Buy Order")

    # --- collect basic inputs first (to keep DB code cleaner) ---
    try:
        pid = int(ask("Portfolio ID"))
    except ValueError:
        raise ValidationError("Portfolio ID must be an integer.")

    ticker = ask("Ticker").upper()
    if not ticker:
        raise ValidationError("Ticker is required.")

    price_mode = ask("Use reference price? (y/n)").lower()
    if price_mode not in {"y", "n"}:
        raise ValidationError("Answer must be 'y' or 'n'.")

    try:
        quantity = int(ask("Quantity to buy"))
    except ValueError:
        raise ValidationError("Quantity must be an integer.")
    if quantity <= 0:
        raise ValidationError("Quantity must be positive.")

    with get_session() as session:
        # validate portfolio ownership
        portfolio = _get_portfolio(session, pid)
        if portfolio.owner_username != current_user.username:
            raise AuthorizationError("You can only buy into your own portfolios.")

        # validate security
        security = _get_security(session, ticker)

        # determine price
        if price_mode == "y":
            price = float(security.price)
        else:
            try:
                price = float(ask("Price per unit"))
            except ValueError:
                raise ValidationError("Price must be a number.")
            if price < 0:
                raise ValidationError("Price must be non-negative.")

        cost = price * quantity

        # load owner user
        user = session.get(User, portfolio.owner_username)
        if user is None:
            raise NotFoundError("Owner user not found.")

        if cost > user.balance:
            raise ValidationError("Insufficient balance to complete purchase.")

        # deduct cash
        user.balance -= cost

        # try to find an existing investment in this portfolio for this ticker
        investment = session.scalars(
            select(Investment).where(
                Investment.portfolio_id == portfolio.id,
                Investment.security_ticker == ticker,  # <-- FIXED
            )
        ).first()

        if investment is None:
            # create a new investment position
            investment = Investment(
                portfolio_id=portfolio.id,
                security_ticker=ticker,   # <-- FIXED
                quantity=quantity,
                avg_price=price,          # <-- FIXED
            )
            session.add(investment)
            session.flush()  # ensure id is assigned before referencing it
        else:
            # update existing position with weighted average price
            total_cost_old = investment.avg_price * investment.quantity
            total_cost_new = total_cost_old + cost
            new_qty = investment.quantity + quantity
            investment.quantity = new_qty
            investment.avg_price = total_cost_new / new_qty  # <-- FIXED

        # record transaction
        tx = Transaction(
            type="BUY",
            username=user.username,
            portfolio_id=portfolio.id,
            investment_id=investment.id,
            security_ticker=ticker,
            quantity=quantity,
            price=price,
            subtotal=cost,
        )
        session.add(tx)

        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            # router will catch this as "Unexpected error"
            raise ValidationError(f"Database error while placing order: {e}")

    print("✅ Purchase recorded.")
    pause()
