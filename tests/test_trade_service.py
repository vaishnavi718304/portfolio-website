from unittest.mock import patch

import pytest

from app.models import Investment, Portfolio, Transaction, User
from app.service.trade_service import InsufficientFundsError, TradeExecutionException, execute_purchase_order, liquidate_investment


def _seed_trade_owner(db_session):
    owner = User(
        username='service_owner',
        password='secret',
        firstname='Service',
        lastname='Owner',
        balance=5000.0,
    )
    db_session.add(owner)
    db_session.flush()

    portfolio = Portfolio(
        name='Service Trade Portfolio',
        description='Portfolio for trade service tests',
        user=owner,
    )
    db_session.add(portfolio)
    db_session.commit()

    return owner, portfolio


def test_execute_purchase_order_creates_investment_and_transaction(db_session):
    owner, portfolio = _seed_trade_owner(db_session)

    with patch(
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
        execute_purchase_order(portfolio.id, 'AAPL', 2)
        db_session.commit()

    refreshed_owner = db_session.query(User).filter_by(username=owner.username).one()
    assert refreshed_owner.balance == 4700.0

    refreshed_portfolio = db_session.query(Portfolio).filter_by(id=portfolio.id).one()
    assert len(refreshed_portfolio.investments) == 1
    assert refreshed_portfolio.investments[0].ticker == 'AAPL'
    assert refreshed_portfolio.investments[0].quantity == 2

    transactions = db_session.query(Transaction).filter_by(portfolio_id=portfolio.id).all()
    assert len(transactions) == 1
    assert transactions[0].transaction_type == 'BUY'
    assert transactions[0].ticker == 'AAPL'
    assert transactions[0].quantity == 2
    assert transactions[0].price == 150.0


def test_execute_purchase_order_invalid_ticker_raises(db_session):
    _, portfolio = _seed_trade_owner(db_session)

    with patch('app.service.trade_service.get_quote', return_value=None):
        with pytest.raises(TradeExecutionException) as exc:
            execute_purchase_order(portfolio.id, 'INVALID', 1)

    assert 'does not exist' in str(exc.value)


def test_execute_purchase_order_insufficient_funds_raises(db_session):
    owner, portfolio = _seed_trade_owner(db_session)
    owner.balance = 10.0
    db_session.commit()

    with patch(
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
        with pytest.raises(InsufficientFundsError) as exc:
            execute_purchase_order(portfolio.id, 'AAPL', 1)

    assert 'Insufficient funds' in str(exc.value)


def test_liquidate_investment_insufficient_holdings_raises(db_session):
    _, portfolio = _seed_trade_owner(db_session)

    db_session.add(Investment(ticker='AAPL', quantity=1, portfolio=portfolio))
    db_session.commit()

    with pytest.raises(TradeExecutionException) as exc:
        liquidate_investment(portfolio.id, 'AAPL', 5, 155.0)

    assert 'Only 1 shares available' in str(exc.value)


def test_liquidate_investment_creates_transaction_and_updates_holding(db_session):
    owner, portfolio = _seed_trade_owner(db_session)

    db_session.add(Investment(ticker='AAPL', quantity=3, portfolio=portfolio))
    db_session.commit()

    liquidate_investment(portfolio.id, 'AAPL', 2, 155.0)
    db_session.commit()

    refreshed_owner = db_session.query(User).filter_by(username=owner.username).one()
    assert refreshed_owner.balance == 5310.0

    refreshed_portfolio = db_session.query(Portfolio).filter_by(id=portfolio.id).one()
    assert len(refreshed_portfolio.investments) == 1
    assert refreshed_portfolio.investments[0].ticker == 'AAPL'
    assert refreshed_portfolio.investments[0].quantity == 1

    transactions = db_session.query(Transaction).filter_by(portfolio_id=portfolio.id).all()
    assert len(transactions) == 1
    assert transactions[0].transaction_type == 'SELL'
    assert transactions[0].ticker == 'AAPL'
    assert transactions[0].quantity == 2
    assert transactions[0].price == 155.0