# app/services/portfolio_service.py
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.domain.user import User
from app.domain.portfolio import Portfolio
from app.domain.security import Security
from app.domain.investment import Investment
from app.domain.transaction import Transaction
from app.domain.exceptions import (
    ValidationError,
    AuthorizationError,
    NotFoundError,
    PortfolioNotEmptyError,
)


def get_all_portfolios() -> List[Portfolio]:
    return db.session.scalars(select(Portfolio)).all()


def get_portfolio_by_id(portfolio_id: int) -> Portfolio:
    p = db.session.get(Portfolio, portfolio_id)
    if p is None:
        raise NotFoundError("Portfolio not found.")
    return p


def create_portfolio(name: str, description: str, owner_username: str) -> Portfolio:
    if not owner_username:
        raise ValidationError("owner_username is required.")
    if not name:
        raise ValidationError("name is required.")

    owner = db.session.get(User, owner_username)
    if owner is None:
        raise NotFoundError("Owner user not found.")

    p = Portfolio(name=name, description=description, owner_username=owner_username)

    try:
        db.session.add(p)
        db.session.commit()
        return p
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValidationError(f"Database error while creating portfolio: {e}")


def delete_portfolio(portfolio_id: int, requesting_username: str) -> None:
    p = get_portfolio_by_id(portfolio_id)

    if not requesting_username:
        raise ValidationError("requesting_username is required.")
    if p.owner_username != requesting_username:
        raise AuthorizationError("You can only delete your own portfolios.")

    # if any investments exist, block delete (same behavior as your CLI version)
    if p.investments and len(p.investments) > 0:
        raise PortfolioNotEmptyError(
            "Portfolio has investments. Please liquidate all holdings before deleting."
        )

    try:
        db.session.delete(p)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValidationError(f"Database error while deleting portfolio: {e}")


def add_security_to_portfolio(
    portfolio_id: int,
    requesting_username: str,
    ticker: str,
    quantity: float,
    purchase_price: float,
) -> Investment:
    if not requesting_username:
        raise ValidationError("requesting_username is required.")
    if not ticker:
        raise ValidationError("ticker is required.")
    if quantity <= 0:
        raise ValidationError("quantity must be positive.")
    if purchase_price < 0:
        raise ValidationError("purchase_price must be non-negative.")

    p = get_portfolio_by_id(portfolio_id)
    if p.owner_username != requesting_username:
        raise AuthorizationError("You can only modify your own portfolios.")

    user = db.session.get(User, requesting_username)
    if user is None:
        raise NotFoundError("User not found.")

    sec = db.session.get(Security, ticker)
    if sec is None:
        raise NotFoundError("Security not found. Add it to the securities table first.")

    subtotal = purchase_price * quantity
    if user.balance < subtotal:
        raise ValidationError("Insufficient cash balance to buy this quantity.")

    inv = db.session.scalars(
        select(Investment).where(
            Investment.portfolio_id == portfolio_id,
            Investment.security_ticker == ticker,
        )
    ).first()

    if inv is None:
        inv = Investment(
            portfolio_id=portfolio_id,
            security_ticker=ticker,
            quantity=0.0,
            avg_price=0.0,
        )
        db.session.add(inv)

    # weighted average price update
    old_qty = float(inv.quantity)
    old_avg = float(inv.avg_price)
    new_qty = old_qty + float(quantity)
    if new_qty > 0:
        inv.avg_price = ((old_qty * old_avg) + (float(quantity) * float(purchase_price))) / new_qty
    inv.quantity = new_qty

    user.balance -= subtotal

    db.session.flush()  # ensures inv.id is populated before we use it


    tx = Transaction(
        type="BUY",
        username=user.username,
        portfolio_id=portfolio_id,
        investment_id=inv.id,  # will be set after flush/commit
        security_ticker=ticker,
        quantity=quantity,
        price=purchase_price,
        subtotal=subtotal,
    )
    db.session.add(tx)

    try:
        db.session.commit()
        return inv
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValidationError(f"Database error while adding security: {e}")


def harvest_investment(
    portfolio_id: int,
    requesting_username: str,
    ticker: str,
    quantity: float,
    sale_price: float,
) -> None:
    if not requesting_username:
        raise ValidationError("requesting_username is required.")
    if not ticker:
        raise ValidationError("ticker is required.")
    if quantity <= 0:
        raise ValidationError("quantity must be positive.")
    if sale_price < 0:
        raise ValidationError("sale_price must be non-negative.")

    p = get_portfolio_by_id(portfolio_id)
    if p.owner_username != requesting_username:
        raise AuthorizationError("You can only modify your own portfolios.")

    user = db.session.get(User, requesting_username)
    if user is None:
        raise NotFoundError("User not found.")

    inv = db.session.scalars(
        select(Investment).where(
            Investment.portfolio_id == portfolio_id,
            Investment.security_ticker == ticker,
        )
    ).first()

    if inv is None or inv.quantity <= 0:
        raise NotFoundError("This portfolio does not hold that ticker.")
    if quantity > inv.quantity:
        raise ValidationError("Insufficient position to sell that quantity.")

    inv.quantity = float(inv.quantity) - float(quantity)

    subtotal = float(sale_price) * float(quantity)
    user.balance += subtotal

    tx = Transaction(
        type="SELL",
        username=user.username,
        portfolio_id=portfolio_id,
        investment_id=inv.id,
        security_ticker=ticker,
        quantity=quantity,
        price=sale_price,
        subtotal=subtotal,
    )
    db.session.add(tx)

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValidationError(f"Database error while harvesting investment: {e}")
