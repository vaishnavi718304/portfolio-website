from unittest.mock import patch

from app.auth.auth import AuthError


def test_protected_route_returns_403_when_token_missing(client):
    response = client.get('/users/')

    assert response.status_code == 403
    body = response.get_json()
    assert body['error'] == 'Forbidden'
    assert 'bearer token' in body['detail'].lower()


def test_protected_route_returns_403_when_token_expired(client):
    with patch('app.auth.auth.validate_token', side_effect=AuthError('Token has expired')):
        response = client.get(
            '/users/',
            headers={'Authorization': 'Bearer expired-token'},
        )

    assert response.status_code == 403
    body = response.get_json()
    assert body['error'] == 'Forbidden'
    assert body['detail'] == 'Token has expired'


def test_protected_route_returns_403_when_token_invalid(client):
    with patch('app.auth.auth.validate_token', side_effect=AuthError('Token is invalid')):
        response = client.get(
            '/users/',
            headers={'Authorization': 'Bearer invalid-token'},
        )

    assert response.status_code == 403
    body = response.get_json()
    assert body['error'] == 'Forbidden'
    assert body['detail'] == 'Token is invalid'


def test_protected_route_allows_access_with_valid_token(client):
    with patch('app.auth.auth.validate_token', return_value={'username': 'admin'}):
        response = client.get(
            '/users/',
            headers={'Authorization': 'Bearer valid-token'},
        )

    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, list)
    assert any(user['username'] == 'admin' for user in body)