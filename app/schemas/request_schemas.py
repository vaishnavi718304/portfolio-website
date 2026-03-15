from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    error: str
    detail: str


class CreateUserRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    username: str = Field(min_length=1, max_length=30)
    password: str = Field(min_length=1, max_length=30)
    firstname: str = Field(min_length=1, max_length=30)
    lastname: str = Field(min_length=1, max_length=30)
    balance: float = Field(ge=0)


class UpdateBalanceRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    username: str = Field(min_length=1, max_length=30)
    new_balance: float = Field(ge=0)


class CreatePortfolioRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    username: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=30)
    description: str = Field(min_length=1, max_length=500)


class AssignPortfolioAccessRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    username: str = Field(min_length=1, max_length=30)
    role: str = Field(min_length=1, max_length=20)


class BuyTradeRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    ticker: str = Field(min_length=1, max_length=10)
    portfolio_id: int = Field(gt=0)
    quantity: float = Field(gt=0)


class SellTradeRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    ticker: str = Field(min_length=1, max_length=10)
    portfolio_id: int = Field(gt=0)
    quantity: float = Field(gt=0)
    sale_price: float = Field(gt=0)