# app/routes/portfolios.py
from flask import Blueprint, jsonify, request

from app.domain.exceptions import (
    ValidationError,
    AuthorizationError,
    NotFoundError,
    PortfolioNotEmptyError,
)
from app.services.portfolio_service import (
    get_all_portfolios,
    get_portfolio_by_id,
    create_portfolio,
    delete_portfolio,
    add_security_to_portfolio,
    harvest_investment,
)

portfolio_bp = Blueprint("portfolios", __name__, url_prefix="/portfolios")


def _portfolio_to_dict(p):
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "owner_username": p.owner_username,
    }


@portfolio_bp.get("")
def api_get_all_portfolios():
    portfolios = get_all_portfolios()
    return jsonify([_portfolio_to_dict(p) for p in portfolios]), 200


@portfolio_bp.get("/<int:portfolio_id>")
def api_get_portfolio_by_id(portfolio_id: int):
    try:
        p = get_portfolio_by_id(portfolio_id)
        return jsonify(_portfolio_to_dict(p)), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404


@portfolio_bp.post("")
def api_create_portfolio():
    data = request.get_json(silent=True) or {}
    try:
        p = create_portfolio(
            name=data.get("name", ""),
            description=data.get("description", ""),
            owner_username=data.get("owner_username", ""),
        )
        return jsonify(_portfolio_to_dict(p)), 201
    except (ValidationError, NotFoundError) as e:
        return jsonify({"error": str(e)}), 400


@portfolio_bp.delete("/<int:portfolio_id>")
def api_delete_portfolio(portfolio_id: int):
    data = request.get_json(silent=True) or {}
    try:
        delete_portfolio(
            portfolio_id=portfolio_id,
            requesting_username=data.get("requesting_username", ""),
        )
        return jsonify({"message": "Portfolio deleted."}), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except (ValidationError, AuthorizationError, PortfolioNotEmptyError) as e:
        return jsonify({"error": str(e)}), 400


@portfolio_bp.post("/<int:portfolio_id>/add-security")
def api_add_security(portfolio_id: int):
    data = request.get_json(silent=True) or {}
    try:
        inv = add_security_to_portfolio(
            portfolio_id=portfolio_id,
            requesting_username=data.get("requesting_username", ""),
            ticker=(data.get("ticker", "") or "").upper(),
            quantity=float(data.get("quantity", 0)),
            purchase_price=float(data.get("purchase_price", 0)),
        )
        return jsonify(
            {
                "message": "Security added/updated in portfolio.",
                "investment": {
                    "id": inv.id,
                    "portfolio_id": inv.portfolio_id,
                    "ticker": inv.security_ticker,
                    "quantity": inv.quantity,
                    "avg_price": inv.avg_price,
                },
            }
        ), 200
    except ValueError:
        return jsonify({"error": "quantity and purchase_price must be numbers"}), 400
    except (ValidationError, AuthorizationError, NotFoundError) as e:
        return jsonify({"error": str(e)}), 400


@portfolio_bp.post("/<int:portfolio_id>/harvest")
def api_harvest(portfolio_id: int):
    data = request.get_json(silent=True) or {}
    try:
        harvest_investment(
            portfolio_id=portfolio_id,
            requesting_username=data.get("requesting_username", ""),
            ticker=(data.get("ticker", "") or "").upper(),
            quantity=float(data.get("quantity", 0)),
            sale_price=float(data.get("sale_price", 0)),
        )
        return jsonify({"message": "Harvest (SELL) recorded."}), 200
    except ValueError:
        return jsonify({"error": "quantity and sale_price must be numbers"}), 400
    except (ValidationError, AuthorizationError, NotFoundError) as e:
        return jsonify({"error": str(e)}), 400
