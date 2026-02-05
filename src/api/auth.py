from flask import Blueprint, request, jsonify
from flask_login import current_user
import jwt
from datetime import datetime, timedelta
from src.services.auth_service import AuthService
from src.core.constants import UserRole
from config import Config

api_auth = Blueprint("api_auth", __name__, url_prefix="/api/auth")


@api_auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    success, message, user = AuthService.register_user(name, email, phone, password)

    if success and user:
        token = jwt.encode(
            {"user_id": user.id, "exp": datetime.utcnow() + timedelta(hours=24)},
            Config.JWT_SECRET_KEY,
            algorithm="HS256",
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": message,
                    "user": user.to_dict(),
                    "token": token,
                }
            ),
            201,
        )
    else:
        return jsonify({"success": False, "message": message}), 400


@api_auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = AuthService.get_user_by_email(email)
    if not user or not user.check_password(password):
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"success": False, "message": "Account deactivated"}), 403

    user.last_login = datetime.utcnow()
    from src.core.extensions import db

    db.session.commit()

    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.utcnow() + timedelta(hours=24)},
        Config.JWT_SECRET_KEY,
        algorithm="HS256",
    )

    return (
        jsonify(
            {
                "success": True,
                "message": "Login successful",
                "user": user.to_dict(),
                "token": token,
            }
        ),
        200,
    )


@api_auth.route("/verify", methods=["POST"])
def verify_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"success": False, "message": "No token provided"}), 401

    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        user = AuthService.get_user_by_id(payload["user_id"])

        if user and user.is_active:
            return jsonify({"success": True, "user": user.to_dict()}), 200
        else:
            return jsonify({"success": False, "message": "Invalid token"}), 401
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, IndexError):
        return jsonify({"success": False, "message": "Invalid or expired token"}), 401
