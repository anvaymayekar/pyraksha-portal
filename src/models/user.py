from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from src.core.extensions import db
from src.core.constants import UserRole


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default=UserRole.USER.value, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Complaints filed by the user
    complaints = db.relationship(
        "Complaint",
        foreign_keys="Complaint.user_id",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # Complaints resolved by the user (admin)
    resolved_complaints = db.relationship(
        "Complaint",
        foreign_keys="Complaint.resolved_by",
        lazy="dynamic",
    )

    # SOS events raised by the user
    sos_events = db.relationship(
        "SOS",
        foreign_keys="SOS.user_id",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # SOS events resolved by the user (admin)
    resolved_sos_events = db.relationship(
        "SOS",
        foreign_keys="SOS.resolved_by",
        back_populates="resolver",
        lazy="dynamic",
    )

    # Location history of the user
    locations = db.relationship(
        "Location",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN.value

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active,
        }
