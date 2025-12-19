# app/domain/security.py
from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import db  # ✅ Flask-SQLAlchemy db


if TYPE_CHECKING:
    from app.domain.investment import Investment
    from app.domain.transaction import Transaction


class Security(db.Model):
    __tablename__ = "securities"

    ticker: Mapped[str] = mapped_column(String(10), primary_key=True)
    issuer: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    investments: Mapped[List["Investment"]] = relationship(
        "Investment",
        back_populates="security",
        lazy="selectin",
    )

    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="security",
        lazy="selectin",
    )

    def __str__(self) -> str:
        return f"Security(ticker={self.ticker!r}, issuer={self.issuer!r}, price={self.price:.2f})"
