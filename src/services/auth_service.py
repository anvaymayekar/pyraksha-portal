from datetime import datetime
from typing import Optional, Tuple
from flask_login import login_user, logout_user
from src.core.extensions import db
from src.models.user import User
from src.core.constants import UserRole
import uuid


class AuthService:
    @staticmethod
    def register_user(
        name: str,
        email: str,
        phone: str,
        password: str,
        role: str = UserRole.USER.value,
    ) -> Tuple[bool, str, Optional[User]]:
        if not all([name, email, phone, password]):
            return False, "All fields are required", None

        if len(password) < 6:
            return False, "Password must be at least 6 characters", None

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return False, "Email already registered", None

        user = User(
            user_id=str(uuid.uuid4()), name=name, email=email, phone=phone, role=role
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            return True, "Registration successful", user
        except Exception as e:
            db.session.rollback()
            return False, f"Registration failed: {str(e)}", None

    @staticmethod
    def login_user_service(
        email: str, password: str, remember: bool = False
    ) -> Tuple[bool, str, Optional[User]]:
        if not email or not password:
            return False, "Email and password are required", None

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return False, "Invalid email or password", None

        if not user.is_active:
            return False, "Account is deactivated", None

        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user, remember=remember)
        return True, "Login successful", user

    @staticmethod
    def logout_user_service() -> None:
        logout_user()

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        return User.query.filter_by(email=email).first()

    @staticmethod
    def change_password(
        user: User, old_password: str, new_password: str
    ) -> Tuple[bool, str]:
        if not user.check_password(old_password):
            return False, "Current password is incorrect"

        if len(new_password) < 6:
            return False, "New password must be at least 6 characters"

        user.set_password(new_password)
        db.session.commit()
        return True, "Password changed successfully"

    @staticmethod
    def update_user_profile(
        user: User, name: Optional[str] = None, phone: Optional[str] = None
    ) -> Tuple[bool, str]:
        try:
            if name:
                user.name = name
            if phone:
                user.phone = phone
            db.session.commit()
            return True, "Profile updated successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Update failed: {str(e)}"
