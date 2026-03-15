from unittest.mock import Mock, patch

from app.cache import cache
from app.service.alpha_vantage_client import get_company_name, get_price_data, get_quote


def test_get_company_name_success(app):
    with app.app_context():
        cache.clear()

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'Name': 'Apple Inc.'}

        with patch('app.service.alpha_vantage_client.requests.get', return_value=mock_response) as mock_get:
            company_name = get_company_name('AAPL')

        assert company_name == 'Apple Inc.'
        mock_get.assert_called_once()


def test_get_company_name_returns_none_when_missing(app):
    with app.app_context():
        cache.clear()

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}

        with patch('app.service.alpha_vantage_client.requests.get', return_value=mock_response):
            company_name = get_company_name('AAPL')

        assert company_name is None


def test_get_company_name_uses_cache(app):
    with app.app_context():
        cache.clear()
        cache.set('company_name:AAPL', 'Apple Inc.')

        with patch('app.service.alpha_vantage_client.requests.get') as mock_get:
            company_name = get_company_name('AAPL')

        assert company_name == 'Apple Inc.'
        mock_get.assert_not_called()


def test_get_price_data_success(app):
    with app.app_context():
        cache.clear()

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'Time Series (Daily)': {
                '2026-03-06': {
                    '1. open': '100.00',
                    '2. high': '105.00',
                    '3. low': '99.00',
                    '4. close': '104.50',
                    '5. volume': '1234567',
                }
            }
        }

        with patch('app.service.alpha_vantage_client.requests.get', return_value=mock_response) as mock_get:
            price_data = get_price_data('AAPL')

        assert price_data == {
            'date': '2026-03-06',
            'open': 100.0,
            'high': 105.0,
            'low': 99.0,
            'close': 104.5,
            'volume': 1234567.0,
        }
        mock_get.assert_called_once()


def test_get_price_data_returns_none_when_missing(app):
    with app.app_context():
        cache.clear()

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}

        with patch('app.service.alpha_vantage_client.requests.get', return_value=mock_response):
            price_data = get_price_data('AAPL')

        assert price_data is None


def test_get_price_data_uses_cache(app):
    with app.app_context():
        cache.clear()
        cache.set(
            'price_data:AAPL',
            {
                'date': '2026-03-06',
                'open': 100.0,
                'high': 105.0,
                'low': 99.0,
                'close': 104.5,
                'volume': 1234567.0,
            },
        )

        with patch('app.service.alpha_vantage_client.requests.get') as mock_get:
            price_data = get_price_data('AAPL')

        assert price_data['close'] == 104.5
        mock_get.assert_not_called()


def test_get_quote_success(app):
    with app.app_context():
        cache.clear()

        overview_response = Mock()
        overview_response.raise_for_status.return_value = None
        overview_response.json.return_value = {'Name': 'Apple Inc.'}

        price_response = Mock()
        price_response.raise_for_status.return_value = None
        price_response.json.return_value = {
            'Time Series (Daily)': {
                '2026-03-06': {
                    '1. open': '100.00',
                    '2. high': '105.00',
                    '3. low': '99.00',
                    '4. close': '104.50',
                    '5. volume': '1234567',
                }
            }
        }

        with patch(
            'app.service.alpha_vantage_client.requests.get',
            side_effect=[overview_response, price_response],
        ):
            quote = get_quote('AAPL')

        assert quote is not None
        assert quote.ticker == 'AAPL'
        assert quote.issuer == 'Apple Inc.'
        assert quote.date == '2026-03-06'
        assert quote.price == 104.5


def test_get_quote_returns_none_when_unresolved(app):
    with app.app_context():
        cache.clear()

        overview_response = Mock()
        overview_response.raise_for_status.return_value = None
        overview_response.json.return_value = {}

        price_response = Mock()
        price_response.raise_for_status.return_value = None
        price_response.json.return_value = {}

        with patch(
            'app.service.alpha_vantage_client.requests.get',
            side_effect=[overview_response, price_response],
        ):
            quote = get_quote('AAPL')

        assert quote is None