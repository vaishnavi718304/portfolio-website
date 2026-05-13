from __future__ import annotations

from functools import wraps

import jwt
import requests
from flask import current_app, g, request
from jwt import ExpiredSignatureError, InvalidTokenError
from jwt.algorithms import RSAAlgorithm
from werkzeug.exceptions import Forbidden

from app.cache import cache


class AuthError(Exception):
    pass


def _get_cognito_region() -> str:
    region = current_app.config.get('COGNITO_REGION', '')
    if not region:
        raise AuthError('COGNITO_REGION is not configured')
    return region


def _get_cognito_user_pool_id() -> str:
    user_pool_id = current_app.config.get('COGNITO_USER_POOL_ID', '')
    if not user_pool_id:
        raise AuthError('COGNITO_USER_POOL_ID is not configured')
    return user_pool_id


def _get_cognito_app_client_id() -> str:
    app_client_id = current_app.config.get('COGNITO_APP_CLIENT_ID', '')
    if not app_client_id:
        raise AuthError('COGNITO_APP_CLIENT_ID is not configured')
    return app_client_id


def _get_issuer() -> str:
    return f'https://cognito-idp.{_get_cognito_region()}.amazonaws.com/{_get_cognito_user_pool_id()}'


def _get_jwks_url() -> str:
    return f'{_get_issuer()}/.well-known/jwks.json'


def _get_jwks() -> dict:
    cache_key = f'cognito_jwks:{_get_issuer()}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    response = requests.get(_get_jwks_url(), timeout=10)
    response.raise_for_status()
    jwks = response.json()

    cache.set(cache_key, jwks)
    return jwks


def _get_signing_key(token: str):
    try:
        header = jwt.get_unverified_header(token)
    except InvalidTokenError as exc:
        raise AuthError('Invalid token header') from exc

    kid = header.get('kid')
    alg = header.get('alg')

    if alg != 'RS256':
        raise AuthError('Unsupported token signing algorithm')
    if not kid:
        raise AuthError('Token header is missing kid')

    jwks = _get_jwks()
    keys = jwks.get('keys', [])

    for jwk in keys:
        if jwk.get('kid') == kid:
            return RSAAlgorithm.from_jwk(jwk)

    raise AuthError('Signing key not found for token')


def validate_token(token: str) -> dict:
    signing_key = _get_signing_key(token)

    try:
        unverified_claims = jwt.decode(token, options={'verify_signature': False})
    except InvalidTokenError as exc:
        raise AuthError('Invalid token claims') from exc

    token_use = unverified_claims.get('token_use')
    issuer = _get_issuer()
    client_id = _get_cognito_app_client_id()

    try:
        if token_use == 'id':
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=['RS256'],
                issuer=issuer,
                audience=client_id,
            )
        elif token_use == 'access':
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=['RS256'],
                issuer=issuer,
                options={'verify_aud': False},
            )
            if claims.get('client_id') != client_id:
                raise AuthError('Invalid access token audience')
        else:
            raise AuthError('Unsupported token_use claim')
    except ExpiredSignatureError as exc:
        raise AuthError('Token has expired') from exc
    except InvalidTokenError as exc:
        raise AuthError('Token is invalid') from exc

    return claims


def extract_identity(claims: dict) -> str:
    identity = (
        claims.get('cognito:username')
        or claims.get('username')
        or claims.get('sub')
    )
    if not identity:
        raise AuthError('Unable to extract authenticated user identity')
    return identity


def authenticate_request() -> None:
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        raise Forbidden('Missing or invalid bearer token')

    token = auth_header.removeprefix('Bearer ').strip()
    if not token:
        raise Forbidden('Missing or invalid bearer token')

    try:
        claims = validate_token(token)
        g.current_user = extract_identity(claims)
        g.jwt_claims = claims
    except AuthError as exc:
        raise Forbidden(str(exc)) from exc
    except Exception as exc:
        raise Forbidden('Authentication failed') from exc


def require_auth(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        authenticate_request()
        return view_func(*args, **kwargs)

    return wrapper