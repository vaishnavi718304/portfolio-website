LOGIN_MENU = "0"
MAIN_MENU = "1"
USERS_MENU = "1.1"
PORTFOLIOS_MENU = "1.2"
MARKET_MENU = "1.3"

MENU_TITLES = {
    LOGIN_MENU: "Login Menu",
    MAIN_MENU: "Main Menu",
    USERS_MENU: "Manage Users",
    PORTFOLIOS_MENU: "Manage Portfolios",
    MARKET_MENU: "Marketplace",
}

# menu actions (ids -> label)
ACTIONS = {
    LOGIN_MENU: {
        "1": "Login",
        "2": "Exit",
    },
    MAIN_MENU: {
        "1.1": "Manage Users (admin only)",
        "1.2": "Manage Portfolios",
        "1.3": "Marketplace",
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
        "1.2.3": "Sell Investment (stub)",
        "1.2.9": "Back",
    },
    MARKET_MENU: {
        "1.3.1": "View Securities",
        "1.3.2": "Buy Security (stub)",
        "1.3.9": "Back",
    },
}
