import time
from dataclasses import dataclass

import requests
from flask import current_app

from app.cache import cache


@dataclass
class SecurityQuote:
    ticker: str
    date: str
    price: float
    issuer: str


class AlphaVantageClientError(Exception):
    pass


def _get_api_key() -> str:
    api_key = current_app.config.get('ALPHA_VANTAGE_API_KEY', '')
    if not api_key:
        raise RuntimeError('ALPHA_VANTAGE_API_KEY is not configured')
    return api_key


def _request_json(params: dict, retries: int = 2, sleep_seconds: float = 1.2) -> dict:
    last_payload = None

    for attempt in range(retries + 1):
        response = requests.get(
            current_app.config['ALPHA_VANTAGE_BASE_URL'],
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        last_payload = payload

        # Alpha Vantage may return a rate-limit/info payload instead of the expected data
        if 'Information' in payload or 'Note' in payload:
            if attempt < retries:
                time.sleep(sleep_seconds)
                continue
            raise AlphaVantageClientError(payload.get('Information') or payload.get('Note'))

        if 'Error Message' in payload:
            raise AlphaVantageClientError(payload['Error Message'])

        return payload

    raise AlphaVantageClientError(f'Unexpected Alpha Vantage response: {last_payload}')


def get_company_name(ticker: str) -> str | None:
    normalized_ticker = (ticker or '').strip().upper()
    if not normalized_ticker:
        return None

    cache_key = f'company_name:{normalized_ticker}'
    cached_value = cache.get(cache_key)
    if cached_value is not None:
        return cached_value

    payload = _request_json(
        {
            'function': 'OVERVIEW',
            'symbol': normalized_ticker,
            'apikey': _get_api_key(),
        }
    )

    company_name = payload.get('Name')
    if not company_name:
        return None

    cache.set(cache_key, company_name)
    return company_name


def get_price_data(ticker: str) -> dict | None:
    normalized_ticker = (ticker or '').strip().upper()
    if not normalized_ticker:
        return None

    cache_key = f'price_data:{normalized_ticker}'
    cached_value = cache.get(cache_key)
    if cached_value is not None:
        return cached_value

    payload = _request_json(
        {
            'function': 'TIME_SERIES_DAILY',
            'symbol': normalized_ticker,
            'outputsize': 'compact',
            'apikey': _get_api_key(),
        }
    )

    time_series = payload.get('Time Series (Daily)')
    if not time_series:
        return None

    latest_date = max(time_series.keys())
    latest_bar = time_series.get(latest_date, {})

    price_data = {
        'date': latest_date,
        'open': float(latest_bar['1. open']),
        'high': float(latest_bar['2. high']),
        'low': float(latest_bar['3. low']),
        'close': float(latest_bar['4. close']),
        'volume': float(latest_bar['5. volume']),
    }

    cache.set(cache_key, price_data)
    return price_data


def get_quote(ticker: str) -> SecurityQuote | None:
    normalized_ticker = (ticker or '').strip().upper()
    if not normalized_ticker:
        return None

    company_name = get_company_name(normalized_ticker)
    price_data = get_price_data(normalized_ticker)

    if company_name is None or price_data is None:
        return None

    return SecurityQuote(
        ticker=normalized_ticker,
        date=price_data['date'],
        price=price_data['close'],
        issuer=company_name,
    )