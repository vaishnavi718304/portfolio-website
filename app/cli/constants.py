# app/cli/constants.py

LOGIN_MENU = "0"
MAIN_MENU = "1"
USERS_MENU = "1.1"
PORTFOLIOS_MENU = "1.2"
MARKET_MENU = "1.3"
TRANSACTIONS_MENU = "1.4"  # NEW

MENU_TITLES = {
    LOGIN_MENU: "Login Menu",
    MAIN_MENU: "Main Menu",
    USERS_MENU: "Manage Users",
    PORTFOLIOS_MENU: "Manage Portfolios",
    MARKET_MENU: "Marketplace",
    TRANSACTIONS_MENU: "View Transactions",  # NEW
}

ACTIONS = {
    LOGIN_MENU: {
        "1": "Login",
        "2": "Exit",
    },
    MAIN_MENU: {
        "1.1": "Manage Users (admin only)",
        "1.2": "Manage Portfolios",
        "1.3": "Marketplace",
        "1.4": "View Transactions",  # NEW
        "1.9": "Logout",
    },
    USERS_MENU: {
        "1.1.1": "View Users",
        "1.1.2": "Create User",
        "1.1.3": "Delete User",
        "1.1.9": "Back",
    },
    PORTFOLIOS_MENU: {
        "1.2.1": "View Portfolios",
        "1.2.2": "Create Portfolio",
        "1.2.3": "Delete Portfolio",
        "1.2.4": "Harvest Investment",
        "1.2.5": "View Account Summary",
        "1.2.9": "Back",
    },
    MARKET_MENU: {
        "1.3.1": "View Securities",
        "1.3.2": "Place Buy Order",
        "1.3.9": "Back",
    },
    TRANSACTIONS_MENU: {  # NEW
        "1.4.1": "View ALL my transactions",
        "1.4.2": "View by Portfolio ID",
        "1.4.3": "View by Security Ticker",
        "1.4.9": "Back",
    },
}
