# app/routes/users.py
from flask import Blueprint, jsonify, request

from app.domain.exceptions import ValidationError, NotFoundError
from app.services.user_service import (
    get_all_users,
    get_user_by_username,
    create_user,
    delete_user,
)

user_bp = Blueprint("users", __name__, url_prefix="/users")


def _user_to_dict(u):
    # Do NOT return password
    return {
        "username": u.username,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "role": u.role,
        "balance": u.balance,
    }


@user_bp.get("")
def api_get_all_users():
    users = get_all_users()
    return jsonify([_user_to_dict(u) for u in users]), 200


@user_bp.get("/<string:username>")
def api_get_user_by_id(username: str):
    try:
        user = get_user_by_username(username)
        return jsonify(_user_to_dict(user)), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404


@user_bp.post("")
def api_create_user():
    data = request.get_json(silent=True) or {}

    try:
        user = create_user(
            username=data.get("username", ""),
            password=data.get("password", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            role=data.get("role", "user"),
            balance=float(data.get("balance", 0.0)),
        )
        return jsonify(_user_to_dict(user)), 201
    except ValueError:
        return jsonify({"error": "balance must be a number"}), 400
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400


@user_bp.delete("/<string:username>")
def api_delete_user(username: str):
    data = request.get_json(silent=True) or {}
    requesting_username = data.get("requesting_username")

    try:
        delete_user(username=username, requesting_username=requesting_username)
        return jsonify({"message": "User deleted."}), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
