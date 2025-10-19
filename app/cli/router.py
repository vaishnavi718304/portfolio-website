# app/cli/router.py
from dataclasses import dataclass
from typing import Callable, Optional, Dict, Any

from app.cli.constants import (
    LOGIN_MENU, MAIN_MENU, USERS_MENU, PORTFOLIOS_MENU, MARKET_MENU
)
from app.services import auth, users, portfolios, marketplace


@dataclass(frozen=True)
class Route:
    """
    A route says:
      - executor: the function to run for this action (gets current_user; may return updated user)
      - next_menu: which menu to show after success (None means exit app)
      - on_error_menu: which menu to show if executor raises (ValueError, etc.)
      - precondition: optional guard (e.g., 'is_admin') that must return True for the action to proceed
    """
    executor: Callable[[Optional[Dict[str, Any]]], Optional[Dict[str, Any]]]
    next_menu: Optional[str]
    on_error_menu: str
    precondition: Optional[Callable[[Optional[Dict[str, Any]]], bool]] = None


def _exit_app(_: Optional[Dict[str, Any]]) -> None:
    """Clean, explicit exit used by the Login -> Exit action."""
    raise SystemExit(0)


# Map action-id -> Route
ROUTES: Dict[str, Route] = {
    # --- Login menu ---
    "0.1": Route(executor=auth.login, next_menu=MAIN_MENU, on_error_menu=LOGIN_MENU),
    "0.9": Route(executor=_exit_app, next_menu=None, on_error_menu=LOGIN_MENU),
    "0.2": Route(executor=_exit_app, next_menu=None, on_error_menu=LOGIN_MENU),
     
    # --- Main menu ---
    "1.1": Route(executor=lambda u: u, next_menu=USERS_MENU, on_error_menu=MAIN_MENU, precondition=auth.is_admin),
    "1.2": Route(executor=lambda u: u, next_menu=PORTFOLIOS_MENU, on_error_menu=MAIN_MENU),
    "1.3": Route(executor=lambda u: u, next_menu=MARKET_MENU, on_error_menu=MAIN_MENU),
    "1.9": Route(executor=auth.logout, next_menu=LOGIN_MENU, on_error_menu=MAIN_MENU),

    # --- Users submenu (admin only) ---
    "1.1.1": Route(executor=users.view_users,    next_menu=USERS_MENU, on_error_menu=USERS_MENU, precondition=auth.is_admin),
    "1.1.2": Route(executor=users.create_user,   next_menu=USERS_MENU, on_error_menu=USERS_MENU, precondition=auth.is_admin),
    "1.1.3": Route(executor=users.delete_user,   next_menu=USERS_MENU, on_error_menu=USERS_MENU, precondition=auth.is_admin),
    "1.1.9": Route(executor=lambda u: u,         next_menu=MAIN_MENU,  on_error_menu=USERS_MENU),

    # --- Portfolios submenu ---
    "1.2.1": Route(executor=portfolios.view_portfolios, next_menu=PORTFOLIOS_MENU, on_error_menu=PORTFOLIOS_MENU),
    "1.2.2": Route(executor=portfolios.create_portfolio, next_menu=PORTFOLIOS_MENU, on_error_menu=PORTFOLIOS_MENU),
    "1.2.3": Route(executor=portfolios.sell_investment,  next_menu=PORTFOLIOS_MENU, on_error_menu=PORTFOLIOS_MENU),
    "1.2.9": Route(executor=lambda u: u,                 next_menu=MAIN_MENU,       on_error_menu=PORTFOLIOS_MENU),

    # --- Marketplace submenu ---
    "1.3.1": Route(executor=marketplace.list_securities, next_menu=MARKET_MENU, on_error_menu=MARKET_MENU),
    "1.3.2": Route(executor=marketplace.buy_security,    next_menu=MARKET_MENU, on_error_menu=MARKET_MENU),
    "1.3.9": Route(executor=lambda u: u,                 next_menu=MAIN_MENU,   on_error_menu=MARKET_MENU),
}
