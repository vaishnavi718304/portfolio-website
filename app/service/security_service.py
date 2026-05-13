from typing import List

from app.db import db
from app.models import Security
from app.service.alpha_vantage_client import SecurityQuote, get_quote


class SecurityException(Exception):
    pass


def get_all_securities() -> List[SecurityQuote]:
    securities = db.session.query(Security).all()

    quotes: List[SecurityQuote] = []
    for security in securities:
        quote = get_quote(security.ticker)
        if quote is not None:
            quotes.append(quote)

    return quotes


def get_security_by_ticker(ticker: str) -> SecurityQuote | None:
    if not ticker:
        raise SecurityException('Ticker is required.')

    return get_quote(ticker)