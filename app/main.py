# app/main.py
from app.cli.menu_printer import show_menu, get_choice, print_error
from app.cli.router import ROUTES
from app.cli.constants import LOGIN_MENU

def run():
    # current_menu should be the *menu id prefix* used in your routes
    # For the login menu that’s "0" in our router keys ("0.1", "0.2"/"0.9").
    current_menu = "0"
    current_user = None

    while True:
        # draw the menu for the current section
        show_menu(current_menu)

        # read what the user typed (e.g., "1" or "2")
        raw = get_choice().strip()

        # allow both simple numbers ("1") and full hierarchical ids ("0.1")
        if "." in raw:
            route_key = raw
        else:
            route_key = f"{current_menu}.{raw}"

        route = ROUTES.get(route_key)
        if not route:
            print_error("Invalid choice. Try again.")
            continue

        # check preconditions (e.g., admin-only)
        if route.precondition and not route.precondition(current_user):
            print_error("Not authorized.")
            continue

        try:
            # run the action; if it returns a user, update the current session
            result = route.executor(current_user)
            if result is not None:
                current_user = result

            # move to the next menu or exit if None
            if route.next_menu is None:
                print("Goodbye!")
                break
            current_menu = route.next_menu

        except SystemExit:
            # for clean exits triggered by the exit route
            print("Goodbye!")
            break
        except Exception as e:
            # show friendly error and bounce to the on-error menu
            print_error(str(e))
            current_menu = route.on_error_menu
            
if __name__ == "__main__":
    run()
