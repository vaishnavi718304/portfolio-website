# app/main.py
import os

from app import create_app
from app.config import Config
from app.db import db

# import models so db.create_all() sees the tables
import app.domain.user       # noqa: F401
import app.domain.portfolio  # noqa: F401
import app.domain.security   # noqa: F401
import app.domain.investment # noqa: F401
import app.domain.transaction # noqa: F401

app = create_app(Config)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True)
