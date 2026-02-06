from datetime import datetime
from typing import Optional
from src.core.extensions import db
from src.core.constants import ComplaintStatus


class Complaint(db.Model):
    __tablename__ = "complaints"

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.String(20), default=ComplaintStatus.PENDING.value, nullable=False, index=True
    )
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    resolution_notes = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    user = db.relationship("User", foreign_keys=[user_id], back_populates="complaints")
    resolver = db.relationship("User", foreign_keys=[resolved_by])

    def update_status(
        self,
        new_status: str,
        resolved_by_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> None:
        self.status = new_status
        if new_status in [ComplaintStatus.RESOLVED.value, ComplaintStatus.CLOSED.value]:
            self.resolved_at = datetime.utcnow()
            if resolved_by_id:
                self.resolved_by = resolved_by_id
            if notes:
                self.resolution_notes = notes

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "user_id": self.user.user_id if self.user else str(self.user_id),
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "resolution_notes": self.resolution_notes,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    @staticmethod
    def from_dict(data: dict, user_id: int) -> "Complaint":
        return Complaint(
            complaint_id=data.get("complaint_id"),
            user_id=user_id,
            title=data.get("title"),
            description=data.get("description"),
            status=data.get("status", ComplaintStatus.PENDING.value),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
        )

    def __repr__(self) -> str:
        return f"<Complaint {self.complaint_id}>"
