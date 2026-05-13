from typing import List
from app.db import db
from app.models import Portfolio, User
from app.models.Transaction import Transaction


class UnsupportedPortfolioOperationError(Exception):
    pass


class PortfolioOperationError(Exception):
    pass


def create_portfolio(name: str, description: str, user: User) -> int:
    if not name or not description or not user:
        raise UnsupportedPortfolioOperationError(
            f'Invalid input[name:{name}, description:{description}, user:{user}]. Please try again.'
        )
    portfolio = Portfolio(name=name, description=description, user=user)
    db.session.add(portfolio)
    db.session.flush()
    return portfolio.id


def get_portfolios_by_user(user: User) -> List[Portfolio]:
    if not user or not user.username:
        raise UnsupportedPortfolioOperationError('A valid user is required to retrieve portfolios.')
    return db.session.query(Portfolio).filter_by(owner=user.username).all()


def get_all_portfolios() -> List[Portfolio]:
    return db.session.query(Portfolio).all()


def get_portfolio_by_id(portfolio_id: int) -> Portfolio | None:
    return db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()


def delete_portfolio(portfolio_id: int) -> None:
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise UnsupportedPortfolioOperationError(f'Portfolio with id {portfolio_id} does not exist')
    if portfolio.investments and len(portfolio.investments) > 0:
        raise PortfolioOperationError('Cannot delete a portfolio that still contains holdings. Please sell all positions first.')
    db.session.query(Transaction).filter_by(portfolio_id=portfolio_id).delete()
    db.session.delete(portfolio)
    db.session.flush()