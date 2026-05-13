import datetime

from app.db import db
from app.models import Investment, Portfolio, Security, Transaction
from app.service.alpha_vantage_client import get_quote


class TradeExecutionException(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


def execute_purchase_order(portfolio_id: int, ticker: str, quantity: float):
    if portfolio_id is None or not ticker or quantity is None or quantity <= 0:
        raise TradeExecutionException(
            f'Invalid purchase order parameters [portfolio_id={portfolio_id}, ticker={ticker}, quantity={quantity}]'
        )

    normalized_ticker = ticker.strip().upper()

    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise TradeExecutionException(f'Portfolio with id {portfolio_id} does not exist.')

    user = portfolio.user
    if not user:
        raise TradeExecutionException(f'User associated with the portfolio ({portfolio_id}) does not exist.')

    quote = get_quote(normalized_ticker)
    if not quote:
        raise TradeExecutionException(f'Security with ticker {normalized_ticker} does not exist.')

    total_cost = quote.price * quantity
    if user.balance < total_cost:
        raise InsufficientFundsError('Insufficient funds to complete the purchase.')

    security = db.session.query(Security).filter_by(ticker=normalized_ticker).one_or_none()
    if not security:
        security = Security(ticker=quote.ticker, issuer=quote.issuer, price=quote.price)
        db.session.add(security)
        db.session.flush()
    else:
        security.issuer = quote.issuer
        security.price = quote.price

    existing_investment = next((inv for inv in portfolio.investments if inv.ticker == normalized_ticker), None)
    if existing_investment:
        existing_investment.quantity += quantity
    else:
        portfolio.investments.append(Investment(ticker=normalized_ticker, quantity=quantity, security=security))

    user.balance -= total_cost

    db.session.add(
        Transaction(
            portfolio_id=portfolio.id,
            username=user.username,
            ticker=normalized_ticker,
            quantity=quantity,
            price=quote.price,
            transaction_type='BUY',
            date_time=datetime.datetime.now(),
        )
    )
    db.session.flush()


def liquidate_investment(portfolio_id: int, ticker: str, quantity: float, sale_price: float):
    if portfolio_id is None or not ticker or quantity is None or quantity <= 0:
        raise TradeExecutionException(
            f'Invalid liquidation parameters [portfolio_id={portfolio_id}, ticker={ticker}, quantity={quantity}]'
        )

    normalized_ticker = ticker.strip().upper()

    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise TradeExecutionException(f'Portfolio with id {portfolio_id} does not exist')

    user = portfolio.user
    if not user:
        raise TradeExecutionException(f'User associated with the portfolio ({portfolio_id}) does not exist.')

    investment = next((inv for inv in portfolio.investments if inv.ticker == normalized_ticker), None)
    if not investment:
        raise TradeExecutionException(
            f'No investment with ticker {normalized_ticker} exists in portfolio with id {portfolio_id}'
        )

    if investment.quantity < quantity:
        raise TradeExecutionException(
            f'Cannot liquidate {quantity} shares of {normalized_ticker}. '
            f'Only {investment.quantity} shares available in portfolio'
        )

    total_proceeds = sale_price * quantity
    user.balance += total_proceeds

    if investment.quantity == quantity:
        db.session.delete(investment)
    else:
        investment.quantity -= quantity

    db.session.add(
        Transaction(
            portfolio_id=portfolio.id,
            username=user.username,
            ticker=normalized_ticker,
            quantity=quantity,
            price=sale_price,
            transaction_type='SELL',
            date_time=datetime.datetime.now(),
        )
    )
    db.session.flush()