import pytest


def test_create_user_validation_missing_username(client):
    response = client.post(
        '/users/',
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
    response = client.post(
        '/users/',
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
    response = client.post(
        '/users/',
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
    response = client.post(
        '/portfolios/',
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
    response = client.post(
        '/trades/buy',
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
    response = client.post(
        '/trades/buy',
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
    response = client.post(
        '/trades/sell',
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
    response = client.put(
        '/users/update-balance',
        json={
            'username': 'admin',
            'new_balance': -10,
        },
    )

    assert response.status_code == 422
    body = response.get_json()
    assert body['error'] == 'ValidationError'
    assert 'new_balance' in body['detail']
