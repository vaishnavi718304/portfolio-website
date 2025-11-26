from typing import Optional

from app.cli.menu_printer import show_menu, get_choice, print_error
from app.cli.router import ROUTES
from app.cli.constants import LOGIN_MENU
from app.domain.exceptions import AppError
from app.domain.user import User


def run() -> None:
    current_menu: str = LOGIN_MENU
    current_user: Optional[User] = None

    while True:
        show_menu(current_menu)
        raw = get_choice().strip()

        if "." in raw:
            route_key = raw
        else:
            route_key = f"{current_menu}.{raw}"

        route = ROUTES.get(route_key)
        if not route:
            print_error("Invalid choice. Try again.")
            continue

        if route.precondition and not route.precondition(current_user):
            print_error("Not authorized.")
            continue

        try:
            result = route.executor(current_user)
            if result is not None:
                current_user = result

            if route.next_menu is None:
                print("Goodbye!")
                break
            current_menu = route.next_menu

        except SystemExit:
            print("Goodbye!")
            break
        except AppError as e:
            # expected app-level errors (validation, auth, not found, etc.)
            print_error(str(e))
            current_menu = route.on_error_menu
        except Exception as e:
            # unexpected bug – keep app alive but show the real error for debugging
            # print a short message and the full traceback to help locate the issue
            print_error(f"Unexpected error occurred: {e}")
            # print full traceback to stdout so developer can see stack frames
            import traceback

            traceback.print_exc()
            current_menu = route.on_error_menu


if __name__ == "__main__":
    run()
