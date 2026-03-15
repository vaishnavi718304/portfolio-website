from unittest.mock import patch

from app.models import Investment, Portfolio, Transaction, User


def _auth_headers(username: str) -> dict:
    return {'Authorization': f'Bearer {username}-token'}


def _patch_auth(username: str):
    return patch('app.auth.auth.validate_token', return_value={'username': username})


def _seed_owner_portfolio(db_session):
    owner = User(
        username='trade_owner',
        password='secret',
        firstname='Trade',
        lastname='Owner',
        balance=5000.0,
    )
    db_session.add(owner)
    db_session.flush()

    portfolio = Portfolio(
        name='Trade Portfolio',
        description='Portfolio for trade route tests',
        user=owner,
    )
    db_session.add(portfolio)
    db_session.commit()

    return owner, portfolio


def test_buy_trade_route_creates_transaction_and_updates_holdings(client, db_session):
    owner, portfolio = _seed_owner_portfolio(db_session)

    with _patch_auth(owner.username), patch(
        'app.service.trade_service.get_quote',
        return_value=type(
            'Quote',
            (),
            {
                'ticker': 'AAPL',
                'issuer': 'Apple Inc',
                'price': 150.0,
                'date': '2026-03-11',
            },
        )(),
    ):
        response = client.post(
            '/trades/buy',
            headers=_auth_headers(owner.username),
            json={
                'portfolio_id': portfolio.id,
                'ticker': 'AAPL',
                'quantity': 2,
            },
        )

    assert response.status_code == 201

    refreshed_portfolio = db_session.query(Portfolio).filter_by(id=portfolio.id).one()
    assert len(refreshed_portfolio.investments) == 1
    assert refreshed_portfolio.investments[0].ticker == 'AAPL'
    assert refreshed_portfolio.investments[0].quantity == 2

    refreshed_owner = db_session.query(User).filter_by(username=owner.username).one()
    assert refreshed_owner.balance == 4700.0

    transactions = db_session.query(Transaction).filter_by(portfolio_id=portfolio.id).all()
    assert len(transactions) == 1
    assert transactions[0].transaction_type == 'BUY'
    assert transactions[0].ticker == 'AAPL'
    assert transactions[0].quantity == 2
    assert transactions[0].price == 150.0


def test_buy_trade_route_returns_400_for_invalid_ticker(client, db_session):
    owner, portfolio = _seed_owner_portfolio(db_session)

    with _patch_auth(owner.username), patch('app.service.trade_service.get_quote', return_value=None):
        response = client.post(
            '/trades/buy',
            headers=_auth_headers(owner.username),
            json={
                'portfolio_id': portfolio.id,
                'ticker': 'INVALID',
                'quantity': 1,
            },
        )

    assert response.status_code == 400
    body = response.get_json()
    assert body['error'] == 'TradeExecutionException'
    assert 'does not exist' in body['detail']


def test_sell_trade_route_returns_400_for_insufficient_holdings(client, db_session):
    owner, portfolio = _seed_owner_portfolio(db_session)

    db_session.add(Investment(ticker='AAPL', quantity=1, portfolio=portfolio))
    db_session.commit()

    with _patch_auth(owner.username):
        response = client.post(
            '/trades/sell',
            headers=_auth_headers(owner.username),
            json={
                'portfolio_id': portfolio.id,
                'ticker': 'AAPL',
                'quantity': 5,
                'sale_price': 155.0,
            },
        )

    assert response.status_code == 400
    body = response.get_json()
    assert body['error'] == 'TradeExecutionException'
    assert 'Only 1 shares available' in body['detail']


def test_sell_trade_route_creates_transaction_and_reduces_holdings(client, db_session):
    owner, portfolio = _seed_owner_portfolio(db_session)

    db_session.add(Investment(ticker='AAPL', quantity=3, portfolio=portfolio))
    db_session.commit()

    with _patch_auth(owner.username):
        response = client.post(
            '/trades/sell',
            headers=_auth_headers(owner.username),
            json={
                'portfolio_id': portfolio.id,
                'ticker': 'AAPL',
                'quantity': 2,
                'sale_price': 155.0,
            },
        )

    assert response.status_code == 200

    refreshed_portfolio = db_session.query(Portfolio).filter_by(id=portfolio.id).one()
    assert len(refreshed_portfolio.investments) == 1
    assert refreshed_portfolio.investments[0].ticker == 'AAPL'
    assert refreshed_portfolio.investments[0].quantity == 1

    refreshed_owner = db_session.query(User).filter_by(username=owner.username).one()
    assert refreshed_owner.balance == 5310.0

    transactions = db_session.query(Transaction).filter_by(portfolio_id=portfolio.id).all()
    assert len(transactions) == 1
    assert transactions[0].transaction_type == 'SELL'
    assert transactions[0].ticker == 'AAPL'
    assert transactions[0].quantity == 2
    assert transactions[0].price == 155.0