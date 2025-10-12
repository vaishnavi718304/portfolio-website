from typing import Optional, Dict
from app.cli.constants import LOGIN_MENU
from app.cli.menu_printer import show_menu, get_choice, print_error
from app.cli.router import ROUTES

def run():
    current_menu = LOGIN_MENU
    current_user: Optional[Dict] = None

    while True:
        show_menu(current_menu)
        action_id = get_choice()
        route = ROUTES.get(action_id)

        if not route:
            print_error("Invalid choice. Try again.")
            continue

        # precondition (e.g., admin-only sections)
        if route.precondition and not route.precondition(current_user):
            print_error("You are not allowed to do that.")
            next_menu = route.on_error_menu
            current_menu = next_menu
            continue

        try:
            result = route.executor(current_user)
            # auth.login returns a user; other executors ignore return
            if isinstance(result, dict):
                current_user = result
        except SystemExit:
            print("Goodbye!")
            break
        except Exception as e:
            print_error(str(e))
            current_menu = route.on_error_menu
            continue

        if route.next_menu is None:
            break  # exit
        current_menu = route.next_menu

if __name__ == "__main__":
    run()
