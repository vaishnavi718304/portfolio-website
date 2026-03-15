from flask import Blueprint, g, jsonify, request

import app.service.portfolio_access_service as portfolio_access_service
from app.auth import authenticate_request
from app.db import db
from app.schemas import BuyTradeRequest, SellTradeRequest
from app.service import trade_service

trade_bp = Blueprint('trade', __name__)


@trade_bp.route('/buy', methods=['POST'])
def execute_purchase_order():
    payload = BuyTradeRequest.model_validate(request.get_json() or {})
    authenticate_request()

    if not portfolio_access_service.has_portfolio_role(payload.portfolio_id, g.current_user, 'manager'):
        return jsonify({'error': 'Forbidden', 'detail': 'You do not have permission to trade on this portfolio'}), 403

    trade_service.execute_purchase_order(
        portfolio_id=payload.portfolio_id,
        ticker=payload.ticker,
        quantity=payload.quantity,
    )
    db.session.commit()
    return jsonify({'message': 'Purchase order executed successfully'}), 201


@trade_bp.route('/sell', methods=['POST'])
def liquidate_investment():
    payload = SellTradeRequest.model_validate(request.get_json() or {})
    authenticate_request()

    if not portfolio_access_service.has_portfolio_role(payload.portfolio_id, g.current_user, 'manager'):
        return jsonify({'error': 'Forbidden', 'detail': 'You do not have permission to trade on this portfolio'}), 403

    trade_service.liquidate_investment(
        portfolio_id=payload.portfolio_id,
        ticker=payload.ticker,
        quantity=payload.quantity,
        sale_price=payload.sale_price,
    )
    db.session.commit()
    return jsonify({'message': 'Investment liquidated successfully'}), 200