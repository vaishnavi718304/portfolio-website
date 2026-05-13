from unittest.mock import patch


def _patch_auth(username: str = 'admin'):
    return patch('app.auth.auth.validate_token', return_value={'username': username})


def _auth_headers(username: str = 'admin') -> dict:
    return {'Authorization': f'Bearer {username}-token'}


def test_create_user_validation_missing_username(client):
    with _patch_auth():
        response = client.post(
            '/users/',
            headers=_auth_headers(),
            json={
                'password': 'secret',
                'firstname': 'Test',
                'lastname': 'User',
                'balance': 100.0,
            },
        )
    assert response.status_code == 422
    body = response.get_json()
    assert body['error'] == 'ValidationError'
    assert 'username' in body['detail']


def test_create_user_validation_negative_balance(client):
    with _patch_auth():
        response = client.post(
            '/users/',
            headers=_auth_headers(),
            json={
                'username': 'user1',
                'password': 'secret',
                'firstname': 'Test',
                'lastname': 'User',
                'balance': -1,
            },
        )
    assert response.status_code == 422
    body = response.get_json()
    assert body['error'] == 'ValidationError'
    assert 'balance' in body['detail']


def test_create_user_validation_extra_field(client):
    with _patch_auth():
        response = client.post(
            '/users/',
            headers=_auth_headers(),
            json={
                'username': 'user1',
                'password': 'secret',
                'firstname': 'Test',
                'lastname': 'User',
                'balance': 100.0,
                'unexpected': 'x',
            },
        )
    assert response.status_code == 422
    body = response.get_json()
    assert body['error'] == 'ValidationError'


def test_create_portfolio_validation_missing_name(client):
    with _patch_auth():
        response = client.post(
            '/portfolios/',
            headers=_auth_headers(),
            json={
                'username': 'admin',
                'description': 'Test portfolio',
            },
        )
    assert response.status_code == 422
    body = response.get_json()
    assert body['error'] == 'ValidationError'
    assert 'name' in body['detail']


def test_buy_trade_validation_missing_ticker(client):
    with _patch_auth():
        response = client.post(
            '/trades/buy',
            headers=_auth_headers(),
            json={
                'portfolio_id': 1,
                'quantity': 2,
            },
        )
    assert response.status_code == 422
    body = response.get_json()
    assert body['error'] == 'ValidationError'
    assert 'ticker' in body['detail']


def test_buy_trade_validation_invalid_quantity(client):
    with _patch_auth():
        response = client.post(
            '/trades/buy',
            headers=_auth_headers(),
            json={
                'portfolio_id': 1,
                'ticker': 'AAPL',
                'quantity': 0,
            },
        )
    assert response.status_code == 422
    body = response.get_json()
    assert body['error'] == 'ValidationError'
    assert 'quantity' in body['detail']


def test_sell_trade_validation_missing_sale_price(client):
    with _patch_auth():
        response = client.post(
            '/trades/sell',
            headers=_auth_headers(),
            json={
                'portfolio_id': 1,
                'ticker': 'AAPL',
                'quantity': 1,
            },
        )
    assert response.status_code == 422
    body = response.get_json()
    assert body['error'] == 'ValidationError'
    assert 'sale_price' in body['detail']


def test_update_balance_validation_negative_new_balance(client):
    with _patch_auth():
        response = client.put(
            '/users/update-balance',
            headers=_auth_headers(),
            json={
                'username': 'admin',
                'new_balance': -10,
            },
        )
    assert response.status_code == 422
    body = response.get_json()
    assert body['error'] == 'ValidationError'
    assert 'new_balance' in body['detail']
    