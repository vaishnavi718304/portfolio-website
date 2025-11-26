# tests/conftest.py
from __future__ import annotations

import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Make 'app' importable when running pytest from project root ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Now we can import from app.*
import app.database as database
from app.domain.base import Base
from app.domain.user import User
from app.domain.security import Security
from app.domain.portfolio import Portfolio
from app.domain.investment import Investment


# ---------- DB + session setup ----------

@pytest.fixture
def engine():
    """
    Per-test SQLite in-memory engine.

    Each test gets a brand-new database:
      - tables created from Base.metadata
      - discarded after the test
    """
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session(engine):
    """
    Session bound to the SQLite engine, used only for seeding data.
    Services will use app.database.get_session, which we override below
    to return sessions bound to the same engine.
    """
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    with SessionLocal() as session:
        yield session
        # no rollback here; committed seed data should be visible
        # to other sessions inside the same test


@pytest.fixture(autouse=True)
def override_get_session(engine, monkeypatch):
    """
    Automatically override get_session everywhere so that BOTH:
      - app.database.get_session
      - get_session imported inside service modules
    all use the same in-memory SQLite DB.
    """
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)

    def _get_session():
        # Used like:  with get_session() as session:
        return SessionLocal()

    # 1) Patch the central database module
    monkeypatch.setattr(database, "get_session", _get_session)

    # 2) Patch all service modules that imported get_session directly
    from app.services import auth, marketplace, portfolios, transactions, users

    # auth might not call get_session often, but patch anyway
    monkeypatch.setattr(auth, "get_session", _get_session, raising=False)
    monkeypatch.setattr(marketplace, "get_session", _get_session)
    monkeypatch.setattr(portfolios, "get_session", _get_session)
    monkeypatch.setattr(transactions, "get_session", _get_session)
    monkeypatch.setattr(users, "get_session", _get_session)


# ---------- Global pause() patch ----------

@pytest.fixture(autouse=True)
def no_pause(monkeypatch):
    """
    Disable pause() everywhere so tests don't try to read from stdin.
    """
    from app.utils import io as io_mod
    monkeypatch.setattr(io_mod, "pause", lambda: None)

    # Services imported pause directly, so patch their copies too
    from app.services import users, marketplace, portfolios, transactions

    monkeypatch.setattr(users, "pause", lambda: None)
    monkeypatch.setattr(marketplace, "pause", lambda: None)
    monkeypatch.setattr(portfolios, "pause", lambda: None)
    monkeypatch.setattr(transactions, "pause", lambda: None)


# ---------- Common seed data ----------

@pytest.fixture
def seed_data(db_session):
    """
    Seed common test data:

    - admin (role=admin)
    - vaishnavi (role=user)
    - 2 portfolios (one per user)
    - 3 securities (AAPL, MSFT, TSLA)
    - one initial investment for vaishnavi in AAPL (5 shares)
    """
    admin = User(
        username="admin",
        password="admin123",
        first_name="System",
        last_name="Admin",
        role="admin",
        balance=10_000.0,
    )
    user = User(
        username="vaishnavi",
        password="vaishnavi123",
        first_name="Vaish",
        last_name="Y",
        role="user",
        balance=2_000.0,
    )

    db_session.add_all([admin, user])
    db_session.flush()

    user_portfolio = Portfolio(
        name="UserPort",
        description="User test portfolio",
        owner_username=user.username,
    )
    admin_portfolio = Portfolio(
        name="AdminPort",
        description="Admin test portfolio",
        owner_username=admin.username,
    )

    db_session.add_all([user_portfolio, admin_portfolio])
    db_session.flush()

    aapl = Security(ticker="AAPL", issuer="Apple Inc.", price=190.0)
    msft = Security(ticker="MSFT", issuer="Microsoft Corp.", price=340.0)
    tsla = Security(ticker="TSLA", issuer="Tesla, Inc.", price=220.0)

    db_session.add_all([aapl, msft, tsla])
    db_session.flush()

    # Initial holding for the user: 5 AAPL @ 190
    user_inv_aapl = Investment(
        portfolio_id=user_portfolio.id,
        ticker="AAPL",
        quantity=5,
        purchase_price=190.0,
    )
    db_session.add(user_inv_aapl)

    db_session.commit()

    return {
        "admin": admin,
        "user": user,
        "admin_portfolio": admin_portfolio,
        "user_portfolio": user_portfolio,
        "aapl": aapl,
        "msft": msft,
        "tsla": tsla,
        "user_investment_aapl": user_inv_aapl,
    }
