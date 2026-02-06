from datetime import datetime
from typing import Optional, List
from src.core.extensions import db
from src.core.constants import SOSStatus


class SOS(db.Model):
    __tablename__ = "sos"

    id = db.Column(db.Integer, primary_key=True)
    sos_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    status = db.Column(
        db.String(20), default=SOSStatus.ACTIVE.value, nullable=False, index=True
    )
    start_time = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    end_time = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    notes = db.Column(db.Text)

    user = db.relationship("User", foreign_keys=[user_id], back_populates="sos_events")
    resolver = db.relationship("User", foreign_keys=[resolved_by])
    location_history = db.relationship(
        "Location", back_populates="sos", lazy="dynamic", cascade="all, delete-orphan"
    )

    def activate(self) -> None:
        self.status = SOSStatus.ACTIVE.value
        self.start_time = datetime.utcnow()
        self.end_time = None

    def resolve(
        self, resolved_by_id: Optional[int] = None, notes: Optional[str] = None
    ) -> None:
        self.status = SOSStatus.RESOLVED.value
        self.end_time = datetime.utcnow()
        if resolved_by_id:
            self.resolved_by = resolved_by_id
        if notes:
            self.notes = notes

    def get_duration_seconds(self) -> int:
        if self.end_time:
            delta = self.end_time - self.start_time
        else:
            delta = datetime.utcnow() - self.start_time
        return int(delta.total_seconds())

    def get_latest_location(self):
        return self.location_history.order_by(Location.timestamp.desc()).first()

    def to_dict(self, include_locations: bool = False) -> dict:
        data = {
            "id": self.id,
            "sos_id": self.sos_id,
            "user_id": self.user.user_id if self.user else str(self.user_id),
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "resolved_by": self.resolved_by,
            "notes": self.notes,
            "duration_seconds": self.get_duration_seconds(),
        }

        if include_locations:
            data["location_history"] = [
                loc.to_dict() for loc in self.location_history.all()
            ]
        else:
            latest = self.get_latest_location()
            data["latest_location"] = latest.to_dict() if latest else None

        return data

    @staticmethod
    def from_dict(data: dict, user_id: int) -> "SOS":
        return SOS(
            sos_id=data.get("sos_id"),
            user_id=user_id,
            status=data.get("status", SOSStatus.ACTIVE.value),
        )

    def __repr__(self) -> str:
        return f"<SOS {self.sos_id} - {self.status}>"
