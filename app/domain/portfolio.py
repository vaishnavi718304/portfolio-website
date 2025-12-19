# app/domain/portfolio.py
from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import db  # ✅ Flask-SQLAlchemy db


if TYPE_CHECKING:
    from app.domain.user import User
    from app.domain.investment import Investment
    from app.domain.transaction import Transaction


class Portfolio(db.Model):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    owner_username: Mapped[str] = mapped_column(
        ForeignKey("user.username"),
        nullable=False,
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="portfolios",
        lazy="selectin",
    )

    investments: Mapped[List["Investment"]] = relationship(
        "Investment",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="portfolio",
        lazy="selectin",
    )

    def __str__(self) -> str:
        return f"Portfolio(id={self.id}, name={self.name!r}, owner={self.owner_username!r})"
