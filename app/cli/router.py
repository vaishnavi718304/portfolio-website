# app/cli/router.py
from dataclasses import dataclass
from typing import Callable, Optional, Dict

from app.cli.constants import (
    LOGIN_MENU,
    MAIN_MENU,
    USERS_MENU,
    PORTFOLIOS_MENU,
    MARKET_MENU,
    TRANSACTIONS_MENU,  # NEW
)
from app.services import auth, users, portfolios, marketplace
from app.services import transactions as tx_service  # NEW
from app.domain.user import User


@dataclass(frozen=True)
class Route:
    executor: Callable[[Optional[User]], Optional[User]]
    next_menu: Optional[str]
    on_error_menu: str
    precondition: Optional[Callable[[Optional[User]], bool]] = None


def _exit_app(_: Optional[User]) -> None:
    raise SystemExit(0)


ROUTES: Dict[str, Route] = {
    # Login menu
    "0.1": Route(executor=auth.login, next_menu=MAIN_MENU, on_error_menu=LOGIN_MENU),
    "0.2": Route(executor=_exit_app, next_menu=None, on_error_menu=LOGIN_MENU),

    # Main menu
    "1.1": Route(
        executor=lambda u: u,
        next_menu=USERS_MENU,
        on_error_menu=MAIN_MENU,
        precondition=auth.is_admin,
    ),
    "1.2": Route(
        executor=lambda u: u,
        next_menu=PORTFOLIOS_MENU,
        on_error_menu=MAIN_MENU,
    ),
    "1.3": Route(
        executor=lambda u: u,
        next_menu=MARKET_MENU,
        on_error_menu=MAIN_MENU,
    ),
    # NEW: Transactions main-menu entry
    "1.4": Route(
        executor=lambda u: u,
        next_menu=TRANSACTIONS_MENU,
        on_error_menu=MAIN_MENU,
    ),
    "1.9": Route(
        executor=auth.logout,
        next_menu=LOGIN_MENU,
        on_error_menu=MAIN_MENU,
    ),

    # Users submenu
    "1.1.1": Route(
        executor=users.view_users,
        next_menu=USERS_MENU,
        on_error_menu=USERS_MENU,
        precondition=auth.is_admin,
    ),
    "1.1.2": Route(
        executor=users.create_user,
        next_menu=USERS_MENU,
        on_error_menu=USERS_MENU,
        precondition=auth.is_admin,
    ),
    "1.1.3": Route(
        executor=users.delete_user,
        next_menu=USERS_MENU,
        on_error_menu=USERS_MENU,
        precondition=auth.is_admin,
    ),
    "1.1.9": Route(
        executor=lambda u: u,
        next_menu=MAIN_MENU,
        on_error_menu=USERS_MENU,
    ),

    # Portfolios submenu
    "1.2.1": Route(
        executor=portfolios.view_portfolios,
        next_menu=PORTFOLIOS_MENU,
        on_error_menu=PORTFOLIOS_MENU,
    ),
    "1.2.2": Route(
        executor=portfolios.create_portfolio,
        next_menu=PORTFOLIOS_MENU,
        on_error_menu=PORTFOLIOS_MENU,
    ),
    "1.2.3": Route(
        executor=portfolios.delete_portfolio,
        next_menu=PORTFOLIOS_MENU,
        on_error_menu=PORTFOLIOS_MENU,
    ),
    "1.2.4": Route(
        executor=portfolios.harvest_investment,
        next_menu=PORTFOLIOS_MENU,
        on_error_menu=PORTFOLIOS_MENU,
    ),
    "1.2.5": Route(
        executor=portfolios.view_account_summary,
        next_menu=PORTFOLIOS_MENU,
        on_error_menu=PORTFOLIOS_MENU,
    ),
    "1.2.9": Route(
        executor=lambda u: u,
        next_menu=MAIN_MENU,
        on_error_menu=PORTFOLIOS_MENU,
    ),

    # Marketplace submenu
    "1.3.1": Route(
        executor=marketplace.list_securities,
        next_menu=MARKET_MENU,
        on_error_menu=MARKET_MENU,
    ),
    "1.3.2": Route(
        executor=marketplace.buy_security,
        next_menu=MARKET_MENU,
        on_error_menu=MARKET_MENU,
    ),
    "1.3.9": Route(
        executor=lambda u: u,
        next_menu=MAIN_MENU,
        on_error_menu=MARKET_MENU,
    ),

    # Transactions submenu (NEW)
    "1.4.1": Route(
        executor=tx_service.view_user_transactions,
        next_menu=TRANSACTIONS_MENU,
        on_error_menu=TRANSACTIONS_MENU,
    ),
    "1.4.2": Route(
        executor=tx_service.view_portfolio_transactions,
        next_menu=TRANSACTIONS_MENU,
        on_error_menu=TRANSACTIONS_MENU,
    ),
    "1.4.3": Route(
        executor=tx_service.view_security_transactions,
        next_menu=TRANSACTIONS_MENU,
        on_error_menu=TRANSACTIONS_MENU,
    ),
    "1.4.9": Route(
        executor=lambda u: u,
        next_menu=MAIN_MENU,
        on_error_menu=TRANSACTIONS_MENU,
    ),
}
