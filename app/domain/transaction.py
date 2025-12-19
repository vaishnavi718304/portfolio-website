# app/domain/transaction.py
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from datetime import datetime

from sqlalchemy import Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import db  # ✅ Flask-SQLAlchemy db


if TYPE_CHECKING:
    from app.domain.user import User
    from app.domain.portfolio import Portfolio
    from app.domain.security import Security
    from app.domain.investment import Investment


class Transaction(db.Model):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # "BUY" or "SELL"
    type: Mapped[str] = mapped_column(String(4), nullable=False)

    username: Mapped[str] = mapped_column(
        ForeignKey("user.username"),
        nullable=False,
    )

    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id"),
        nullable=False,
    )

    investment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("investments.id"),
        nullable=True,
    )

    security_ticker: Mapped[str] = mapped_column(
        ForeignKey("securities.ticker"),
        nullable=False,
    )

    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="transactions",
        lazy="selectin",
    )

    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio",
        back_populates="transactions",
        lazy="selectin",
    )

    security: Mapped["Security"] = relationship(
        "Security",
        back_populates="transactions",
        lazy="selectin",
    )

    investment: Mapped[Optional["Investment"]] = relationship(
        "Investment",
        back_populates="transactions",
        lazy="selectin",
    )

    def __str__(self) -> str:
        return (
            f"Transaction(id={self.id}, type={self.type}, "
            f"ticker={self.security_ticker}, qty={self.quantity}, "
            f"price={self.price}, portfolio_id={self.portfolio_id})"
        )
