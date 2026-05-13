import pytest
from pydantic import ValidationError

from app.schemas import (
    AssignPortfolioAccessRequest,
    BuyTradeRequest,
    CreatePortfolioRequest,
    CreateUserRequest,
    SellTradeRequest,
    UpdateBalanceRequest,
)


def test_create_user_request_accepts_valid_input():
    payload = CreateUserRequest.model_validate(
        {
            'username': 'user1',
            'password': 'secret',
            'firstname': 'Test',
            'lastname': 'User',
            'balance': 100.0,
        }
    )

    assert payload.username == 'user1'
    assert payload.balance == 100.0


def test_create_user_request_rejects_missing_username():
    with pytest.raises(ValidationError):
        CreateUserRequest.model_validate(
            {
                'password': 'secret',
                'firstname': 'Test',
                'lastname': 'User',
                'balance': 100.0,
            }
        )


def test_update_balance_request_rejects_negative_balance():
    with pytest.raises(ValidationError):
        UpdateBalanceRequest.model_validate(
            {
                'username': 'user1',
                'new_balance': -1,
            }
        )


def test_create_portfolio_request_accepts_valid_input():
    payload = CreatePortfolioRequest.model_validate(
        {
            'username': 'owner',
            'name': 'My Portfolio',
            'description': 'Test description',
        }
    )

    assert payload.username == 'owner'
    assert payload.name == 'My Portfolio'


def test_buy_trade_request_accepts_float_quantity():
    payload = BuyTradeRequest.model_validate(
        {
            'ticker': 'AAPL',
            'portfolio_id': 1,
            'quantity': 2.5,
        }
    )

    assert payload.ticker == 'AAPL'
    assert payload.quantity == 2.5


def test_buy_trade_request_rejects_missing_ticker():
    with pytest.raises(ValidationError):
        BuyTradeRequest.model_validate(
            {
                'portfolio_id': 1,
                'quantity': 2,
            }
        )


def test_sell_trade_request_rejects_missing_sale_price():
    with pytest.raises(ValidationError):
        SellTradeRequest.model_validate(
            {
                'ticker': 'AAPL',
                'portfolio_id': 1,
                'quantity': 1,
            }
        )


def test_assign_portfolio_access_request_accepts_valid_input():
    payload = AssignPortfolioAccessRequest.model_validate(
        {
            'username': 'viewer_user',
            'role': 'viewer',
        }
    )

    assert payload.username == 'viewer_user'
    assert payload.role == 'viewer'


def test_assign_portfolio_access_request_rejects_extra_field():
    with pytest.raises(ValidationError):
        AssignPortfolioAccessRequest.model_validate(
            {
                'username': 'viewer_user',
                'role': 'viewer',
                'extra': 'not-allowed',
            }
        )