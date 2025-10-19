# app/cli/menu_printer.py
from typing import Dict
from rich.console import Console
from rich.table import Table

from app.cli.constants import MENU_TITLES, ACTIONS

console = Console()


def show_menu(menu_id: str) -> None:
    """Print the menu title and its options using rich."""
    title = MENU_TITLES.get(menu_id, "Menu")
    console.rule(f"[bold]{title}[/bold]")

    table = Table(show_header=False, expand=False, pad_edge=False)
    table.add_column(justify="right", style="bold")
    table.add_column()

    for action_id, label in ACTIONS.get(menu_id, {}).items():
        table.add_row(action_id, label)

    console.print(table)
    console.rule()


def get_choice(prompt: str = "Select an option (enter the id): ") -> str:
    """Read the user’s selection as a string (e.g., '0.1', '1.2.3')."""
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def print_error(message: str) -> None:
    """Pretty error message."""
    console.print(f"[bold red]✖ {message}[/bold red]")
