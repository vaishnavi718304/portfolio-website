from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import db

if TYPE_CHECKING:
    from app.models import Portfolio, User


class PortfolioAccess(db.Model):
    __tablename__ = 'portfolio_access'
    __table_args__ = (
        UniqueConstraint('portfolio_id', 'username', name='uq_portfolio_access_portfolio_user'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portfolio_id: Mapped[int] = mapped_column(Integer, ForeignKey('portfolio.id'), nullable=False)
    username: Mapped[str] = mapped_column(String(30), ForeignKey('user.username'), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    portfolio: Mapped['Portfolio'] = relationship('Portfolio', back_populates='access_grants', lazy='selectin')
    user: Mapped['User'] = relationship('User', back_populates='portfolio_access', lazy='selectin')

    if TYPE_CHECKING:
        def __init__(
            self,
            *,
            portfolio_id: int,
            username: str,
            role: str,
        ) -> None: ...

    def __to_dict__(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'username': self.username,
            'role': self.role,
        }