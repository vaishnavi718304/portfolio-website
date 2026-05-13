from unittest.mock import MagicMock, patch

import pytest

from app.auth.auth import AuthError, extract_identity, validate_token


def _auth_headers(token: str = 'valid-token') -> dict:
    return {'Authorization': f'Bearer {token}'}


# ── Route-level auth tests ─────────────────────────────────────────────────────

def test_protected_route_returns_403_when_token_missing(client):
    response = client.get('/users/')
    assert response.status_code == 403
    body = response.get_json()
    assert body['error'] == 'Forbidden'
    assert 'bearer token' in body['detail'].lower()


def test_protected_route_returns_403_when_token_expired(client):
    with patch('app.auth.auth.validate_token', side_effect=AuthError('Token has expired')):
        response = client.get('/users/', headers=_auth_headers('expired-token'))
    assert response.status_code == 403
    body = response.get_json()
    assert body['error'] == 'Forbidden'
    assert body['detail'] == 'Token has expired'


def test_protected_route_returns_403_when_token_invalid(client):
    with patch('app.auth.auth.validate_token', side_effect=AuthError('Token is invalid')):
        response = client.get('/users/', headers=_auth_headers('invalid-token'))
    assert response.status_code == 403
    body = response.get_json()
    assert body['error'] == 'Forbidden'
    assert body['detail'] == 'Token is invalid'


def test_protected_route_allows_access_with_valid_token(client):
    with patch('app.auth.auth.validate_token', return_value={'username': 'admin'}):
        response = client.get('/users/', headers=_auth_headers('valid-token'))
    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, list)
    assert any(user['username'] == 'admin' for user in body)


# ── validate_token unit tests ──────────────────────────────────────────────────

def test_validate_token_raises_on_expired_signature(app):
    """validate_token raises AuthError when PyJWT raises ExpiredSignatureError."""
    import jwt as pyjwt
    with app.app_context():
        mock_key = MagicMock()
        with patch('app.auth.auth._get_signing_key', return_value=mock_key):
            with patch('app.auth.auth.jwt.decode') as mock_decode:
                # First call (unverified) returns id token_use
                mock_decode.side_effect = [
                    {'token_use': 'id'},
                    pyjwt.ExpiredSignatureError('Signature has expired'),
                ]
                with pytest.raises(AuthError, match='Token has expired'):
                    validate_token('some.expired.token')


def test_validate_token_raises_on_invalid_kid(app):
    """validate_token raises AuthError when kid is not found in JWKS."""
    with app.app_context():
        fake_jwks = {'keys': [{'kid': 'different-kid', 'kty': 'RSA'}]}
        with patch('app.auth.auth._get_jwks', return_value=fake_jwks):
            with patch('app.auth.auth.jwt.get_unverified_header', return_value={'kid': 'missing-kid', 'alg': 'RS256'}):
                with pytest.raises(AuthError, match='Signing key not found'):
                    validate_token('some.token.here')


def test_validate_token_raises_on_wrong_algorithm(app):
    """validate_token raises AuthError when algorithm is not RS256."""
    with app.app_context():
        with patch('app.auth.auth.jwt.get_unverified_header', return_value={'kid': 'some-kid', 'alg': 'HS256'}):
            with pytest.raises(AuthError, match='Unsupported token signing algorithm'):
                validate_token('some.token.here')


def test_validate_token_raises_on_wrong_client_id(app):
    """validate_token raises AuthError when access token client_id does not match."""
    import jwt as pyjwt
    with app.app_context():
        mock_key = MagicMock()
        with patch('app.auth.auth._get_signing_key', return_value=mock_key):
            with patch('app.auth.auth.jwt.decode') as mock_decode:
                mock_decode.side_effect = [
                    {'token_use': 'access'},
                    {'token_use': 'access', 'client_id': 'wrong-client-id'},
                ]
                with pytest.raises(AuthError, match='Invalid access token audience'):
                    validate_token('some.access.token')


def test_validate_token_raises_on_missing_kid(app):
    """validate_token raises AuthError when token header has no kid."""
    with app.app_context():
        with patch('app.auth.auth.jwt.get_unverified_header', return_value={'alg': 'RS256'}):
            with pytest.raises(AuthError, match='missing kid'):
                validate_token('some.token.here')


def test_validate_token_raises_on_unsupported_token_use(app):
    """validate_token raises AuthError for unknown token_use values."""
    import jwt as pyjwt
    with app.app_context():
        mock_key = MagicMock()
        with patch('app.auth.auth._get_signing_key', return_value=mock_key):
            with patch('app.auth.auth.jwt.decode') as mock_decode:
                mock_decode.side_effect = [
                    {'token_use': 'refresh'},
                    {'token_use': 'refresh'},
                ]
                with pytest.raises(AuthError, match='Unsupported token_use'):
                    validate_token('some.refresh.token')


# ── extract_identity unit tests ────────────────────────────────────────────────

def test_extract_identity_from_cognito_username():
    claims = {'cognito:username': 'testuser', 'sub': 'some-uuid'}
    assert extract_identity(claims) == 'testuser'


def test_extract_identity_from_username_claim():
    claims = {'username': 'testuser2', 'sub': 'some-uuid'}
    assert extract_identity(claims) == 'testuser2'


def test_extract_identity_falls_back_to_sub():
    claims = {'sub': 'fallback-uuid'}
    assert extract_identity(claims) == 'fallback-uuid'


def test_extract_identity_raises_when_no_identity():
    with pytest.raises(AuthError, match='Unable to extract'):
        extract_identity({})
