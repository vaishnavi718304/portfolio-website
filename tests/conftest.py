from __future__ import annotations

import sys
from pathlib import Path
from typing import Generator

import pytest

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from app.config import TestConfig
from app.db import db
from app.models import Security, User


@pytest.fixture(scope='function')
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        _populate_database()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app) -> Generator:
    try:
        yield db.session
    finally:
        db.session.rollback()
        db.session.remove()


def _populate_database():
    admin_user = db.session.get(User, 'admin')
    if admin_user is None:
        db.session.add(
            User(
                username='admin',
                password='admin',
                firstname='Admin',
                lastname='User',
                balance=1000.00,
            )
        )

    existing_tickers = {security.ticker for security in db.session.query(Security).all()}
    seed_securities = [
        Security(ticker='AAPL', issuer='Apple Inc.', price=150.00),
        Security(ticker='GOOGL', issuer='Alphabet Inc.', price=2800.00),
        Security(ticker='MSFT', issuer='Microsoft Corp.', price=300.00),
    ]

    for security in seed_securities:
        if security.ticker not in existing_tickers:
            db.session.add(security)

    db.session.commit()