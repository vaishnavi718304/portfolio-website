from flask import Flask, jsonify
from flask_cors import CORS
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.cache import cache
from app.db import db
from app.routes import portfolio_bp, security_bp, trade_bp, user_bp
from app.schemas import ErrorResponse


def _rollback_safely():
    try:
        db.session.rollback()
    except Exception:
        pass


def _error_response(error: str, detail, status_code: int):
    payload = ErrorResponse(error=error, detail=str(detail))
    return jsonify(payload.model_dump()), status_code


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    cache.init_app(app)
    CORS(app)

    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(portfolio_bp, url_prefix='/portfolios')
    app.register_blueprint(security_bp, url_prefix='/securities')
    app.register_blueprint(trade_bp, url_prefix='/trades')

    from app.service.portfolio_access_service import PortfolioAccessError
    from app.service.portfolio_service import PortfolioOperationError, UnsupportedPortfolioOperationError
    from app.service.security_service import SecurityException
    from app.service.trade_service import InsufficientFundsError, TradeExecutionException
    from app.service.user_service import UnsupportedUserOperationError

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        _rollback_safely()
        return _error_response('ValidationError', error, 422)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        _rollback_safely()
        return _error_response(error.name, error.description, error.code)

    def handle_domain_exception(error):
        _rollback_safely()
        return _error_response(error.__class__.__name__, error, 400)

    for exc in (
        UnsupportedPortfolioOperationError,
        PortfolioOperationError,
        PortfolioAccessError,
        SecurityException,
        TradeExecutionException,
        InsufficientFundsError,
        UnsupportedUserOperationError,
    ):
        app.register_error_handler(exc, handle_domain_exception)

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        _rollback_safely()
        return _error_response('InternalServerError', error, 500)

    return app