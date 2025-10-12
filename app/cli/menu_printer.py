from app.cli.constants import MENU_TITLES, ACTIONS

def show_menu(menu_id: str):
    title = MENU_TITLES.get(menu_id, f"Menu {menu_id}")
    print("\n" + "=" * 40)
    print(title)
    print("=" * 40)
    actions = ACTIONS.get(menu_id, {})
    for key, label in actions.items():
        print(f"{key:>6}  {label}")
    print("-" * 40)

def get_choice() -> str:
    return input("Select an option (enter the id): ").strip()

def print_error(message: str):
    print(f"⚠️  {message}")
