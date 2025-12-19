# app/__init__.py
from flask import Flask
from app.db import db

def create_app(config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    # register extensions
    db.init_app(app)

    # register blueprints
    from app.routes.users import user_bp
    from app.routes.portfolios import portfolio_bp
    from app.routes.securities import security_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(security_bp)

    return app
