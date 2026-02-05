from typing import Optional, List, Tuple
from sqlalchemy import or_
from src.core.extensions import db
from src.models.complaint import Complaint
from src.core.constants import ComplaintStatus


class ComplaintService:
    @staticmethod
    def create_complaint(
        user_id: int,
        complaint_id: str,
        title: str,
        description: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Tuple[bool, str, Optional[Complaint]]:
        if not title or not description:
            return False, "Title and description are required", None

        if len(title) < 5:
            return False, "Title must be at least 5 characters", None

        if len(description) < 10:
            return False, "Description must be at least 10 characters", None

        complaint = Complaint(
            complaint_id=complaint_id,
            user_id=user_id,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
        )

        try:
            db.session.add(complaint)
            db.session.commit()
            return True, "Complaint filed successfully", complaint
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to file complaint: {str(e)}", None

    @staticmethod
    def get_user_complaints(
        user_id: int, status: Optional[str] = None, limit: int = 50
    ) -> List[Complaint]:
        query = Complaint.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Complaint.timestamp.desc()).limit(limit).all()

    @staticmethod
    def get_all_complaints(
        status: Optional[str] = None, limit: int = 100
    ) -> List[Complaint]:
        query = Complaint.query
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Complaint.timestamp.desc()).limit(limit).all()

    @staticmethod
    def get_complaint_by_id(complaint_id: str) -> Optional[Complaint]:
        return Complaint.query.filter_by(complaint_id=complaint_id).first()

    @staticmethod
    def update_complaint_status(
        complaint_id: str,
        new_status: str,
        resolved_by_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Tuple[bool, str]:
        complaint = Complaint.query.filter_by(complaint_id=complaint_id).first()
        if not complaint:
            return False, "Complaint not found"

        complaint.update_status(new_status, resolved_by_id, notes)

        try:
            db.session.commit()
            return True, "Complaint status updated"
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to update status: {str(e)}"

    @staticmethod
    def search_complaints(query: str, user_id: Optional[int] = None) -> List[Complaint]:
        search = f"%{query}%"
        base_query = Complaint.query.filter(
            or_(Complaint.title.ilike(search), Complaint.description.ilike(search))
        )

        if user_id:
            base_query = base_query.filter_by(user_id=user_id)

        return base_query.order_by(Complaint.timestamp.desc()).limit(50).all()

    @staticmethod
    def get_complaint_statistics() -> dict:
        total = Complaint.query.count()
        pending = Complaint.query.filter_by(
            status=ComplaintStatus.PENDING.value
        ).count()
        under_review = Complaint.query.filter_by(
            status=ComplaintStatus.UNDER_REVIEW.value
        ).count()
        resolved = Complaint.query.filter_by(
            status=ComplaintStatus.RESOLVED.value
        ).count()
        closed = Complaint.query.filter_by(status=ComplaintStatus.CLOSED.value).count()

        return {
            "total": total,
            "pending": pending,
            "under_review": under_review,
            "resolved": resolved,
            "closed": closed,
        }
