from flask import Blueprint, g, jsonify, request

import app.service.portfolio_access_service as portfolio_access_service
import app.service.portfolio_service as portfolio_service
import app.service.transaction_service as transaction_service
import app.service.user_service as user_service
from app.auth import require_auth
from app.db import db
from app.schemas import AssignPortfolioAccessRequest, CreatePortfolioRequest

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/', methods=['GET'])
@require_auth
def get_all_portfolios():
    portfolios = portfolio_access_service.get_accessible_portfolios_for_user(g.current_user)
    return jsonify([portfolio.__to_dict__() for portfolio in portfolios]), 200


@portfolio_bp.route('/<int:portfolio_id>', methods=['GET'])
@require_auth
def get_portfolio(portfolio_id):
    if not portfolio_access_service.has_portfolio_role(portfolio_id, g.current_user, 'viewer'):
        return jsonify({'error': 'Forbidden', 'detail': 'You do not have access to this portfolio'}), 403

    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404
    return jsonify(portfolio.__to_dict__()), 200


@portfolio_bp.route('/user/<username>', methods=['GET'])
@require_auth
def get_portfolios_by_user(username):
    if g.current_user != username:
        return jsonify({'error': 'Forbidden', 'detail': 'You may only view your own portfolio list'}), 403

    user = user_service.get_user_by_username(username)
    if user is None:
        return jsonify({'error': f'User {username} not found'}), 404

    portfolios = portfolio_access_service.get_accessible_portfolios_for_user(username)
    return jsonify([portfolio.__to_dict__() for portfolio in portfolios]), 200


@portfolio_bp.route('/', methods=['POST'])
@require_auth
def create_portfolio():
    payload = CreatePortfolioRequest.model_validate(request.get_json() or {})

    if g.current_user != payload.username:
        return jsonify({'error': 'Forbidden', 'detail': 'You may only create portfolios for yourself'}), 403

    user = user_service.get_user_by_username(payload.username)
    if user is None:
        return jsonify({'error': f'User {payload.username} not found'}), 404

    portfolio_id = portfolio_service.create_portfolio(
        name=payload.name,
        description=payload.description,
        user=user,
    )
    db.session.commit()
    return jsonify({'message': 'Portfolio created successfully', 'portfolio_id': portfolio_id}), 201


@portfolio_bp.route('/<int:portfolio_id>', methods=['DELETE'])
@require_auth
def delete_portfolio(portfolio_id):
    if not portfolio_access_service.is_portfolio_owner(portfolio_id, g.current_user):
        return jsonify({'error': 'Forbidden', 'detail': 'Only the portfolio owner may delete this portfolio'}), 403

    portfolio_service.delete_portfolio(portfolio_id)
    db.session.commit()
    return jsonify({'message': 'Portfolio deleted successfully'}), 200


@portfolio_bp.route('/<int:portfolio_id>/transactions', methods=['GET'])
@require_auth
def get_portfolio_transactions(portfolio_id):
    if not portfolio_access_service.has_portfolio_role(portfolio_id, g.current_user, 'viewer'):
        return jsonify({'error': 'Forbidden', 'detail': 'You do not have access to this portfolio'}), 403

    transactions = transaction_service.get_transactions_by_portfolio_id(portfolio_id)
    return jsonify([transaction.__to_dict__() for transaction in transactions]), 200


@portfolio_bp.route('/<int:portfolio_id>/access', methods=['POST'])
@require_auth
def grant_portfolio_access(portfolio_id):
    if not portfolio_access_service.is_portfolio_owner(portfolio_id, g.current_user):
        return jsonify({'error': 'Forbidden', 'detail': 'Only the portfolio owner may grant access'}), 403

    payload = AssignPortfolioAccessRequest.model_validate(request.get_json() or {})
    access_grant = portfolio_access_service.grant_portfolio_access(
        portfolio_id=portfolio_id,
        username=payload.username,
        role=payload.role,
    )
    db.session.commit()
    return jsonify({'message': 'Portfolio access granted successfully', 'access': access_grant.__to_dict__()}), 201


@portfolio_bp.route('/<int:portfolio_id>/access/<username>', methods=['DELETE'])
@require_auth
def revoke_portfolio_access(portfolio_id, username):
    if not portfolio_access_service.is_portfolio_owner(portfolio_id, g.current_user):
        return jsonify({'error': 'Forbidden', 'detail': 'Only the portfolio owner may revoke access'}), 403

    portfolio_access_service.revoke_portfolio_access(portfolio_id, username)
    db.session.commit()
    return jsonify({'message': 'Portfolio access revoked successfully'}), 200
