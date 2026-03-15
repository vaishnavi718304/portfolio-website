from app.db import db
from app.models import Portfolio, PortfolioAccess, User


class PortfolioAccessError(Exception):
    pass


VALID_ROLES = {'viewer', 'manager'}


def grant_portfolio_access(portfolio_id: int, username: str, role: str) -> PortfolioAccess:
    normalized_role = (role or '').strip().lower()

    if normalized_role not in VALID_ROLES:
        raise PortfolioAccessError('Role must be either viewer or manager')

    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise PortfolioAccessError(f'Portfolio with id {portfolio_id} does not exist')

    user = db.session.query(User).filter_by(username=username).one_or_none()
    if not user:
        raise PortfolioAccessError(f'User {username} does not exist')

    if portfolio.owner == username:
        raise PortfolioAccessError('Owner does not need an access grant')

    existing_access = (
        db.session.query(PortfolioAccess)
        .filter_by(portfolio_id=portfolio_id, username=username)
        .one_or_none()
    )

    if existing_access:
        existing_access.role = normalized_role
        db.session.flush()
        return existing_access

    access_grant = PortfolioAccess(
        portfolio_id=portfolio_id,
        username=username,
        role=normalized_role,
    )
    db.session.add(access_grant)
    db.session.flush()
    return access_grant


def revoke_portfolio_access(portfolio_id: int, username: str) -> None:
    access_grant = (
        db.session.query(PortfolioAccess)
        .filter_by(portfolio_id=portfolio_id, username=username)
        .one_or_none()
    )

    if not access_grant:
        raise PortfolioAccessError(
            f'Access grant for user {username} on portfolio {portfolio_id} does not exist'
        )

    db.session.delete(access_grant)
    db.session.flush()


def get_portfolio_access(portfolio_id: int, username: str) -> PortfolioAccess | None:
    return (
        db.session.query(PortfolioAccess)
        .filter_by(portfolio_id=portfolio_id, username=username)
        .one_or_none()
    )


def has_portfolio_role(portfolio_id: int, username: str, required_role: str) -> bool:
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        return False

    if portfolio.owner == username:
        return True

    access_grant = get_portfolio_access(portfolio_id, username)
    if not access_grant:
        return False

    if required_role == 'viewer':
        return access_grant.role in {'viewer', 'manager'}
    if required_role == 'manager':
        return access_grant.role == 'manager'

    return False


def is_portfolio_owner(portfolio_id: int, username: str) -> bool:
    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        return False
    return portfolio.owner == username


def get_accessible_portfolios_for_user(username: str) -> list[Portfolio]:
    owned = db.session.query(Portfolio).filter_by(owner=username).all()

    granted = (
        db.session.query(Portfolio)
        .join(PortfolioAccess, PortfolioAccess.portfolio_id == Portfolio.id)
        .filter(PortfolioAccess.username == username)
        .all()
    )

    portfolio_map = {portfolio.id: portfolio for portfolio in owned}
    for portfolio in granted:
        portfolio_map[portfolio.id] = portfolio

    return list(portfolio_map.values())