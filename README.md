## Assignment 2 – Database Integration, Services, and Tests

### 1. Summary of Implemented Features

- Connected the CLI app to a real database using **SQLAlchemy** (`app/database.py`, models in `app/domain/`).
- Added ORM models for:
  - `User`, `Portfolio`, `Security`, `Investment`, and `Transaction`.
- Implemented service-layer logic in `app/services/`:
  - `auth` – login and current-user handling.
  - `marketplace` – list securities, place BUY orders, update holdings & cash, write `Transaction` rows.
  - `portfolios` – create/delete portfolios and harvest (SELL) investments with validation checks.
  - `transactions` – view transactions by user, portfolio, or security.
  - `users` – admin-only user management (create/list/delete users with role and balance checks).
- Wrote a pytest test suite in `tests/` with:
  - An isolated **in-memory SQLite DB** per test (`conftest.py`).
  - Shared `seed_data` fixtures for users, portfolios, securities, and initial AAPL holdings.
  - Tests that cover both **happy paths** and **error branches** (validation, authorization, not-found).

---

### 2. How to Set Up and Run Tests

From the project root:

```bash
# (optional) create and activate a virtualenv first

pip install -r requirements.txt

# run the full test suite with coverage for the app package
pytest --cov=app --cov-report=term-missing
---------- coverage: platform darwin, python 3.9.6-final-0 -----------
Name                        Stmts   Miss  Cover   Missing
--------------------------------------------------------
app/config.py                   2      0   100%
app/database.py                28     10    64%   41, 48-56, 60-61
app/domain/investment.py       29      0   100%
app/domain/portfolio.py        16      1    94%   50
app/domain/security.py         14      1    93%   38
app/domain/transaction.py      24      1    96%   83
app/domain/user.py             17      1    94%   40
app/services/auth.py           17      0   100%
app/services/marketplace.py    92     10    89%   80-81, 102-103, 110, 128-135, 159-160
app/services/portfolios.py    133     61    54%   24, 36-53, 64, 85-86, 92, ...
app/services/transactions.py   55      7    87%   32-34, 86-87, 98, 118
app/services/users.py          79      9    89%   60, 137-146, 151
app/utils/io.py                 7      1    86%   9
--------------------------------------------------------
TOTAL                         527    102    81%
