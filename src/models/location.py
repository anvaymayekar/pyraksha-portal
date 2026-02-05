from datetime import datetime
from typing import Optional
from src.core.extensions import db
from src.core.constants import LocationUpdateType


class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    sos_id = db.Column(db.Integer, db.ForeignKey("sos.id"), nullable=True, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float)
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    update_type = db.Column(db.String(20), default=LocationUpdateType.MANUAL.value)

    user = db.relationship("User", back_populates="locations")
    sos = db.relationship("SOS", back_populates="location_history")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "sos_id": self.sos_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracy": self.accuracy,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "update_type": self.update_type,
        }

    @staticmethod
    def from_dict(data: dict, user_id: int, sos_id: Optional[int] = None) -> "Location":
        return Location(
            user_id=user_id,
            sos_id=sos_id,
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            accuracy=data.get("accuracy"),
            update_type=data.get("update_type", LocationUpdateType.MANUAL.value),
        )

    def __repr__(self) -> str:
        return f"<Location {self.latitude}, {self.longitude}>"
