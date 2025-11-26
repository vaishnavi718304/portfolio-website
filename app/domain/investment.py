# app/domain/investment.py
from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.base import Base


if TYPE_CHECKING:
    from app.domain.portfolio import Portfolio
    from app.domain.security import Security
    from app.domain.transaction import Transaction


class Investment(Base):
    __tablename__ = "investments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id"),
        nullable=False,
    )

    security_ticker: Mapped[str] = mapped_column(
        ForeignKey("securities.ticker"),
        nullable=False,
    )

    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio",
        back_populates="investments",
        lazy="selectin",
    )

    security: Mapped["Security"] = relationship(
        "Security",
        back_populates="investments",
        lazy="selectin",
    )

    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="investment",
        lazy="selectin",
    )

    def __str__(self) -> str:
        return (
            f"Investment(id={self.id}, portfolio_id={self.portfolio_id}, "
            f"ticker={self.security_ticker!r}, qty={self.quantity}, "
            f"avg_price={self.avg_price})"
        )

    # Backwards-compatible aliases used elsewhere in the codebase:
    @property
    def ticker(self) -> str:
        """Alias for security_ticker (used in service modules)."""
        return self.security_ticker

    @ticker.setter
    def ticker(self, value: str) -> None:
        self.security_ticker = value

    @property
    def purchase_price(self) -> float:
        """Alias for avg_price (other modules call this `purchase_price`)."""
        return self.avg_price

    @purchase_price.setter
    def purchase_price(self, value: float) -> None:
        self.avg_price = value
