from functools import wraps
from flask import request, jsonify
import jwt
from config import Config
from src.services.auth_service import AuthService


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"success": False, "message": "Token is missing"}), 401

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            current_user = AuthService.get_user_by_id(payload["user_id"])

            if not current_user or not current_user.is_active:
                return jsonify({"success": False, "message": "Invalid token"}), 401

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, IndexError):
            return (
                jsonify({"success": False, "message": "Invalid or expired token"}),
                401,
            )

        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({"success": False, "message": "Admin access required"}), 403

        return f(current_user, *args, **kwargs)

    return decorated
