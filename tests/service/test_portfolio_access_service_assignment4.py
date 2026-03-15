import pytest

from app.models import Portfolio, PortfolioAccess, User
from app.service.portfolio_access_service import (
    PortfolioAccessError,
    get_accessible_portfolios_for_user,
    get_portfolio_access,
    grant_portfolio_access,
    has_portfolio_role,
    is_portfolio_owner,
    revoke_portfolio_access,
)


def _seed_access_setup(db_session):
    owner = User(
        username='owner',
        password='secret',
        firstname='Owner',
        lastname='User',
        balance=1000.0,
    )
    viewer = User(
        username='viewer',
        password='secret',
        firstname='Viewer',
        lastname='User',
        balance=1000.0,
    )
    manager = User(
        username='manager',
        password='secret',
        firstname='Manager',
        lastname='User',
        balance=1000.0,
    )
    outsider = User(
        username='outsider',
        password='secret',
        firstname='Outsider',
        lastname='User',
        balance=1000.0,
    )

    db_session.add_all([owner, viewer, manager, outsider])
    db_session.flush()

    portfolio = Portfolio(
        name='Owner Portfolio',
        description='Access testing portfolio',
        user=owner,
    )
    db_session.add(portfolio)
    db_session.commit()

    return owner, viewer, manager, outsider, portfolio


def test_grant_portfolio_access_creates_new_grant(db_session):
    _, viewer, _, _, portfolio = _seed_access_setup(db_session)

    grant = grant_portfolio_access(portfolio.id, viewer.username, 'viewer')
    db_session.commit()

    assert grant.username == 'viewer'
    assert grant.role == 'viewer'

    stored = db_session.query(PortfolioAccess).filter_by(
        portfolio_id=portfolio.id,
        username='viewer',
    ).one()
    assert stored.role == 'viewer'


def test_grant_portfolio_access_updates_existing_grant(db_session):
    _, viewer, _, _, portfolio = _seed_access_setup(db_session)

    grant_portfolio_access(portfolio.id, viewer.username, 'viewer')
    db_session.commit()

    updated = grant_portfolio_access(portfolio.id, viewer.username, 'manager')
    db_session.commit()

    assert updated.role == 'manager'

    grants = db_session.query(PortfolioAccess).filter_by(
        portfolio_id=portfolio.id,
        username='viewer',
    ).all()
    assert len(grants) == 1
    assert grants[0].role == 'manager'


def test_grant_portfolio_access_rejects_invalid_role(db_session):
    _, viewer, _, _, portfolio = _seed_access_setup(db_session)

    with pytest.raises(PortfolioAccessError) as exc:
        grant_portfolio_access(portfolio.id, viewer.username, 'admin')

    assert 'viewer or manager' in str(exc.value)


def test_grant_portfolio_access_rejects_missing_portfolio(db_session):
    _seed_access_setup(db_session)

    with pytest.raises(PortfolioAccessError) as exc:
        grant_portfolio_access(9999, 'viewer', 'viewer')

    assert 'does not exist' in str(exc.value)


def test_grant_portfolio_access_rejects_missing_user(db_session):
    *_rest, portfolio = _seed_access_setup(db_session)

    with pytest.raises(PortfolioAccessError) as exc:
        grant_portfolio_access(portfolio.id, 'ghost', 'viewer')

    assert 'does not exist' in str(exc.value)


def test_grant_portfolio_access_rejects_owner(db_session):
    owner, *_rest, portfolio = _seed_access_setup(db_session)

    with pytest.raises(PortfolioAccessError) as exc:
        grant_portfolio_access(portfolio.id, owner.username, 'viewer')

    assert 'Owner does not need an access grant' in str(exc.value)


def test_revoke_portfolio_access_removes_grant(db_session):
    _, viewer, _, _, portfolio = _seed_access_setup(db_session)

    grant_portfolio_access(portfolio.id, viewer.username, 'viewer')
    db_session.commit()

    revoke_portfolio_access(portfolio.id, viewer.username)
    db_session.commit()

    assert get_portfolio_access(portfolio.id, viewer.username) is None


def test_revoke_portfolio_access_raises_when_missing(db_session):
    _seed_access_setup(db_session)

    with pytest.raises(PortfolioAccessError) as exc:
        revoke_portfolio_access(1, 'ghost')

    assert 'does not exist' in str(exc.value)


def test_has_portfolio_role_and_owner_checks(db_session):
    owner, viewer, manager, outsider, portfolio = _seed_access_setup(db_session)

    grant_portfolio_access(portfolio.id, viewer.username, 'viewer')
    grant_portfolio_access(portfolio.id, manager.username, 'manager')
    db_session.commit()

    assert is_portfolio_owner(portfolio.id, owner.username) is True
    assert is_portfolio_owner(portfolio.id, viewer.username) is False

    assert has_portfolio_role(portfolio.id, owner.username, 'viewer') is True
    assert has_portfolio_role(portfolio.id, owner.username, 'manager') is True
    assert has_portfolio_role(portfolio.id, viewer.username, 'viewer') is True
    assert has_portfolio_role(portfolio.id, viewer.username, 'manager') is False
    assert has_portfolio_role(portfolio.id, manager.username, 'viewer') is True
    assert has_portfolio_role(portfolio.id, manager.username, 'manager') is True
    assert has_portfolio_role(portfolio.id, outsider.username, 'viewer') is False
    assert has_portfolio_role(9999, owner.username, 'viewer') is False


def test_get_accessible_portfolios_for_user_returns_owned_and_granted_without_duplicates(db_session):
    owner, viewer, _, _, portfolio = _seed_access_setup(db_session)

    second_portfolio = Portfolio(
        name='Viewer Owned',
        description='Owned by viewer',
        user=viewer,
    )
    db_session.add(second_portfolio)
    db_session.flush()

    grant_portfolio_access(portfolio.id, viewer.username, 'viewer')
    db_session.commit()

    accessible = get_accessible_portfolios_for_user(viewer.username)
    ids = {item.id for item in accessible}

    assert portfolio.id in ids
    assert second_portfolio.id in ids
    assert len(ids) == 2