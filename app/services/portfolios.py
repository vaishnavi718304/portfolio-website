# app/services/portfolios.py
from __future__ import annotations

from typing import Optional, List

from sqlalchemy import select

from app.database import get_session
from app.utils.io import print_header, ask, pause
from app.domain.user import User
from app.domain.portfolio import Portfolio
from app.domain.investment import Investment
from app.domain.exceptions import (
    ValidationError,
    AuthorizationError,
    NotFoundError,
    PortfolioNotEmptyError,
)


def _require_login(current_user: Optional[User]) -> None:
    """Ensure there is a logged-in user."""
    if current_user is None:
        raise AuthorizationError("You must be logged in to perform this action.")


def _portfolio_by_id(session, pid: int) -> Portfolio:
    """Load a portfolio by id or raise NotFoundError."""
    portfolio = session.get(Portfolio, pid)
    if portfolio is None:
        raise NotFoundError("Portfolio not found.")
    return portfolio


def view_portfolios(current_user: Optional[User]) -> None:
    _require_login(current_user)
    print_header("Your Portfolios")

    with get_session() as session:
        portfolios: List[Portfolio] = session.scalars(
            select(Portfolio).where(Portfolio.owner_username == current_user.username)
        ).all()

        if not portfolios:
            print("You have no portfolios yet.")
            pause()
            return

        print(f"{'id':<4} {'name':<20} {'description':<30}")
        for p in portfolios:
            print(f"{p.id:<4} {p.name:<20} {(p.description or ''):<30}")

    pause()


def create_portfolio(current_user: Optional[User]) -> None:
    _require_login(current_user)

    print_header("Create Portfolio")
    name = ask("Portfolio name")
    description = ask("Description")

    if not name:
        raise ValidationError("Portfolio name is required.")

    with get_session() as session:
        portfolio = Portfolio(
            name=name,
            description=description,
            owner_username=current_user.username,
        )
        session.add(portfolio)
        session.commit()
        print(f"✅ Portfolio #{portfolio.id} created.")

    pause()


def delete_portfolio(current_user: Optional[User]) -> None:
    _require_login(current_user)
    print_header("Delete Portfolio")

    try:
        pid = int(ask("Portfolio ID"))
    except ValueError:
        raise ValidationError("Portfolio ID must be an integer.")

    with get_session() as session:
        portfolio = _portfolio_by_id(session, pid)

        if portfolio.owner_username != current_user.username:
            raise AuthorizationError("You can only delete your own portfolios.")

        # uses relationship defined on Portfolio.investments
        if portfolio.investments:
            raise PortfolioNotEmptyError(
                "Portfolio has investments. Please liquidate all holdings before deleting."
            )

        session.delete(portfolio)
        session.commit()
        print("✅ Portfolio deleted.")

    pause()


def harvest_investment(current_user: Optional[User]) -> None:
    """Implements the 'Harvest Investment' (sell) option using the real DB."""
    _require_login(current_user)
    print_header("Harvest Investment")

    try:
        pid = int(ask("Portfolio ID"))
    except ValueError:
        raise ValidationError("Portfolio ID must be an integer.")

    ticker = ask("Ticker").upper()
    if not ticker:
        raise ValidationError("Ticker is required.")

    try:
        quantity = int(ask("Quantity to sell"))
    except ValueError:
        raise ValidationError("Quantity must be an integer.")
    if quantity <= 0:
        raise ValidationError("Quantity must be positive.")

    try:
        sale_price = float(ask("Sale price per unit"))
    except ValueError:
        raise ValidationError("Sale price must be a number.")
    if sale_price < 0:
        raise ValidationError("Sale price must be non-negative.")

    from app.domain.transaction import Transaction  # avoid circular import

    with get_session() as session:
        portfolio = _portfolio_by_id(session, pid)

        if portfolio.owner_username != current_user.username:
            raise AuthorizationError("You can only modify your own portfolios.")

        # existing investment in this portfolio for this ticker
        investment = session.scalars(
            select(Investment).where(
                Investment.portfolio_id == portfolio.id,
                Investment.security_ticker == ticker,  # <-- FIXED
            )
        ).first()

        if investment is None or investment.quantity <= 0:
            raise NotFoundError("This portfolio does not hold that ticker.")

        if quantity > investment.quantity:
            raise ValidationError("Insufficient position to sell that quantity.")

        # reduce investment quantity
        investment.quantity -= quantity

        # NOTE: we KEEP the investment row even if quantity hits 0.
        # This avoids foreign-key issues with Transaction.investment_id
        # and preserves a clean history.

        # credit cash
        user = session.get(User, portfolio.owner_username)
        if user is None:
            raise NotFoundError("Owner user not found.")

        subtotal = sale_price * quantity
        user.balance += subtotal

        tx = Transaction(
            type="SELL",
            username=user.username,
            portfolio_id=portfolio.id,
            investment_id=investment.id,
            security_ticker=ticker,
            quantity=quantity,
            price=sale_price,
            subtotal=subtotal,
        )
        session.add(tx)

        session.commit()
        print("✅ Sale recorded.")

    pause()


def view_account_summary(current_user: Optional[User]) -> None:
    """Show logged-in user's balance, portfolios, and holdings from the DB."""
    _require_login(current_user)
    print_header(f"Account Summary - {current_user.username}")

    with get_session() as session:
        user = session.get(User, current_user.username)
        if user is None:
            raise NotFoundError("User not found.")

        print(f"Name   : {user.first_name} {user.last_name}")
        print(f"Role   : {user.role}")
        print(f"Balance: {user.balance:,.2f}")

        portfolios: List[Portfolio] = session.scalars(
            select(Portfolio).where(Portfolio.owner_username == user.username)
        ).all()

        if not portfolios:
            print("\nYou have no portfolios yet.")
            pause()
            return

        print("\nYour Portfolios:")
        print(f"{'ID':<4} {'Name':<20} {'Description':<30}")
        for p in portfolios:
            print(f"{p.id:<4} {p.name:<20} {(p.description or ''):<30}")

        print("\nHoldings:")
        print(f"{'Portfolio ID':<12} {'Ticker':<8} {'Quantity':>10} {'Avg Price':>12}")
        any_holdings = False

        for p in portfolios:
            invs = session.scalars(
                select(Investment).where(Investment.portfolio_id == p.id)
            ).all()
            for inv in invs:
                any_holdings = True
                print(
                    f"{p.id:<12} {inv.security_ticker:<8} "    # <-- FIXED
                    f"{inv.quantity:>10.2f} {inv.avg_price:>12.2f}"  # <-- FIXED
                )

        if not any_holdings:
            print("(No holdings in any portfolios.)")

    pause()
