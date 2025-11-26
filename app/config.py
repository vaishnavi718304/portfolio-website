
# app/config.py
from typing import Dict, Final

database_config: Final[Dict[str, str]] = {
    "user": "root",              # <- your MySQL username
    "password": "Dalmakhani@11", # <- your MySQL password (the one you type after -p)
    "host": "localhost",         # <- THIS is the bug: must be just "localhost"
    "port": "3306",
    "database": "portfolio_app",
}
