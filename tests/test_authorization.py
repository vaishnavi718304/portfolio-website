from unittest.mock import patch

from app.models import Portfolio, PortfolioAccess, User
from app.service.alpha_vantage_client import SecurityQuote


def _auth_headers(username: str) -> dict:
    return {'Authorization': f'Bearer {username}-token'}


def _patch_auth(username: str):
    return patch('app.auth.auth.validate_token', return_value={'username': username})


def _seed_authorization_data(db_session):
    owner = User(
        username='owner',
        password='secret',
        firstname='Owner',
        lastname='User',
        balance=5000.0,
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
        description='Authorization test portfolio',
        user=owner,
    )
    db_session.add(portfolio)
    db_session.flush()

    db_session.add_all(
        [
            PortfolioAccess(portfolio_id=portfolio.id, username='viewer', role='viewer'),
            PortfolioAccess(portfolio_id=portfolio.id, username='manager', role='manager'),
        ]
    )
    db_session.commit()

    return portfolio


def test_owner_can_view_portfolio(client, db_session):
    portfolio = _seed_authorization_data(db_session)

    with _patch_auth('owner'):
        response = client.get(f'/portfolios/{portfolio.id}', headers=_auth_headers('owner'))

    assert response.status_code == 200
    body = response.get_json()
    assert body['id'] == portfolio.id
    assert body['owner'] == 'owner'


def test_viewer_can_view_but_cannot_trade(client, db_session):
    portfolio = _seed_authorization_data(db_session)

    with _patch_auth('viewer'):
        view_response = client.get(f'/portfolios/{portfolio.id}', headers=_auth_headers('viewer'))
        trade_response = client.post(
            '/trades/buy',
            headers=_auth_headers('viewer'),
            json={
                'portfolio_id': portfolio.id,
                'ticker': 'AAPL',
                'quantity': 1,
            },
        )

    assert view_response.status_code == 200
    assert trade_response.status_code == 403
    assert trade_response.get_json()['error'] == 'Forbidden'


def test_manager_can_trade_but_cannot_delete_portfolio(client, db_session):
    portfolio = _seed_authorization_data(db_session)

    mock_quote = SecurityQuote(
        ticker='AAPL',
        date='2026-05-12',
        price=150.00,
        issuer='Apple Inc.',
    )

    with _patch_auth('manager'):
        with patch('app.service.trade_service.get_quote', return_value=mock_quote):
            trade_response = client.post(
                '/trades/buy',
                headers=_auth_headers('manager'),
                json={
                    'portfolio_id': portfolio.id,
                    'ticker': 'AAPL',
                    'quantity': 1,
                },
            )
        delete_response = client.delete(
            f'/portfolios/{portfolio.id}',
            headers=_auth_headers('manager'),
        )

    assert trade_response.status_code == 201
    assert delete_response.status_code == 403
    assert delete_response.get_json()['error'] == 'Forbidden'


def test_user_with_no_access_gets_403(client, db_session):
    portfolio = _seed_authorization_data(db_session)

    with _patch_auth('outsider'):
        response = client.get(f'/portfolios/{portfolio.id}', headers=_auth_headers('outsider'))

    assert response.status_code == 403
    body = response.get_json()
    assert body['error'] == 'Forbidden'


def test_owner_can_grant_and_revoke_access(client, db_session):
    portfolio = _seed_authorization_data(db_session)

    with _patch_auth('owner'):
        grant_response = client.post(
            f'/portfolios/{portfolio.id}/access',
            headers=_auth_headers('owner'),
            json={
                'username': 'outsider',
                'role': 'viewer',
            },
        )

        revoke_response = client.delete(
            f'/portfolios/{portfolio.id}/access/outsider',
            headers=_auth_headers('owner'),
        )

    assert grant_response.status_code == 201
    assert grant_response.get_json()['access']['username'] == 'outsider'
    assert grant_response.get_json()['access']['role'] == 'viewer'
    assert revoke_response.status_code == 200


def test_manager_cannot_grant_access(client, db_session):
    portfolio = _seed_authorization_data(db_session)

    with _patch_auth('manager'):
        response = client.post(
            f'/portfolios/{portfolio.id}/access',
            headers=_auth_headers('manager'),
            json={
                'username': 'outsider',
                'role': 'viewer',
            },
        )

    assert response.status_code == 403
    assert response.get_json()['error'] == 'Forbidden'


def test_manager_cannot_create_portfolio_for_owner(client, db_session):
    _seed_authorization_data(db_session)

    with _patch_auth('manager'):
        response = client.post(
            '/portfolios/',
            headers=_auth_headers('manager'),
            json={
                'username': 'owner',
                'name': 'Not Allowed',
                'description': 'Manager should not create for owner',
            },
        )

    assert response.status_code == 403
    assert response.get_json()['error'] == 'Forbidden'