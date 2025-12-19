# app/routes/securities.py
from flask import Blueprint, jsonify

from app.services.security_service import get_all_securities

security_bp = Blueprint("securities", __name__, url_prefix="/securities")


def _security_to_dict(s):
    return {"ticker": s.ticker, "issuer": s.issuer, "price": s.price}


@security_bp.get("")
def api_get_all_securities():
    securities = get_all_securities()
    return jsonify([_security_to_dict(s) for s in securities]), 200
