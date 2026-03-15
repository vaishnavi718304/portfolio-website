from unittest.mock import patch

import pytest

from app.models import Security
from app.service.alpha_vantage_client import SecurityQuote
from app.service.security_service import SecurityException, get_all_securities, get_security_by_ticker


def test_get_all_securities_returns_only_resolved_quotes(db_session):
    db_session.add_all(
        [
            Security(ticker='TSLA', issuer='Tesla Inc.', price=200.0),
            Security(ticker='NVDA', issuer='NVIDIA Corp.', price=500.0),
        ]
    )
    db_session.commit()

    with patch(
        'app.service.security_service.get_quote',
        side_effect=lambda ticker: {
            'AAPL': None,
            'GOOGL': None,
            'MSFT': None,
            'TSLA': SecurityQuote(ticker='TSLA', date='2026-03-12', price=210.0, issuer='Tesla Inc.'),
            'NVDA': None,
        }.get(ticker),
    ):
        quotes = get_all_securities()

    assert len(quotes) == 1
    assert quotes[0].ticker == 'TSLA'
    assert quotes[0].price == 210.0


def test_get_security_by_ticker_returns_quote(db_session):
    with patch(
        'app.service.security_service.get_quote',
        return_value=SecurityQuote(ticker='AAPL', date='2026-03-12', price=155.0, issuer='Apple Inc.'),
    ):
        quote = get_security_by_ticker('AAPL')

    assert quote is not None
    assert quote.ticker == 'AAPL'
    assert quote.issuer == 'Apple Inc.'


def test_get_security_by_ticker_raises_for_empty_ticker(db_session):
    with pytest.raises(SecurityException) as exc:
        get_security_by_ticker('')

    assert 'Ticker is required' in str(exc.value)