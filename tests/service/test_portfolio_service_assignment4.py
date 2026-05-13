import pytest

from app.models import Portfolio, User
from app.service.portfolio_service import (
    UnsupportedPortfolioOperationError,
    create_portfolio,
    delete_portfolio,
    get_all_portfolios,
    get_portfolio_by_id,
    get_portfolios_by_user,
)


def _make_user(db_session, username='owner1'):
    user = User(
        username=username,
        password='secret',
        firstname='Owner',
        lastname='User',
        balance=1000.0,
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_create_portfolio_returns_new_id(db_session):
    user = _make_user(db_session, 'portfolio_owner')

    portfolio_id = create_portfolio(
        name='Growth Portfolio',
        description='Long-term holdings',
        user=user,
    )
    db_session.commit()

    created = db_session.query(Portfolio).filter_by(id=portfolio_id).one()
    assert created.name == 'Growth Portfolio'
    assert created.owner == 'portfolio_owner'


def test_create_portfolio_raises_for_invalid_input(db_session):
    user = _make_user(db_session, 'bad_input_owner')

    with pytest.raises(UnsupportedPortfolioOperationError):
        create_portfolio('', 'desc', user)

    with pytest.raises(UnsupportedPortfolioOperationError):
        create_portfolio('name', '', user)

    with pytest.raises(UnsupportedPortfolioOperationError):
        create_portfolio('name', 'desc', None)


def test_get_portfolios_by_user_returns_only_owned_portfolios(db_session):
    user = _make_user(db_session, 'owner_a')
    other = _make_user(db_session, 'owner_b')

    create_portfolio('P1', 'desc1', user)
    create_portfolio('P2', 'desc2', user)
    create_portfolio('Other', 'desc3', other)
    db_session.commit()

    portfolios = get_portfolios_by_user(user)

    names = sorted([portfolio.name for portfolio in portfolios])
    assert names == ['P1', 'P2']


def test_get_portfolios_by_user_raises_for_invalid_user(db_session):
    with pytest.raises(UnsupportedPortfolioOperationError):
        get_portfolios_by_user(None)

    class DummyUser:
        username = ''

    with pytest.raises(UnsupportedPortfolioOperationError):
        get_portfolios_by_user(DummyUser())


def test_get_all_portfolios_returns_created_portfolios(db_session):
    user = _make_user(db_session, 'all_owner')

    create_portfolio('One', 'desc1', user)
    create_portfolio('Two', 'desc2', user)
    db_session.commit()

    portfolios = get_all_portfolios()
    names = [portfolio.name for portfolio in portfolios]

    assert 'One' in names
    assert 'Two' in names


def test_get_portfolio_by_id_returns_none_when_missing(db_session):
    assert get_portfolio_by_id(9999) is None


def test_delete_portfolio_removes_existing_portfolio(db_session):
    user = _make_user(db_session, 'delete_owner')

    portfolio_id = create_portfolio('Delete Me', 'desc', user)
    db_session.commit()

    delete_portfolio(portfolio_id)
    db_session.commit()

    deleted = db_session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    assert deleted is None


def test_delete_portfolio_raises_when_missing(db_session):
    with pytest.raises(UnsupportedPortfolioOperationError) as exc:
        delete_portfolio(9999)

    assert 'does not exist' in str(exc.value)