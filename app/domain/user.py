# app/domain/user.py
from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import db  # ✅ Flask-SQLAlchemy db


if TYPE_CHECKING:
    from app.domain.portfolio import Portfolio
    from app.domain.transaction import Transaction


class User(db.Model):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(30), primary_key=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False, default="user")
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    portfolios: Mapped[List["Portfolio"]] = relationship(
        "Portfolio",
        back_populates="owner",
        lazy="selectin",
    )

    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="user",
        lazy="selectin",
    )

    def __str__(self) -> str:
        return (
            f"<User username={self.username}; "
            f"name={self.first_name} {self.last_name}; "
            f"balance={self.balance}>"
        )
