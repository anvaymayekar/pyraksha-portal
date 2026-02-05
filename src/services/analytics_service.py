from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import func
from src.core.extensions import db
from src.models.user import User
from src.models.sos import SOS
from src.models.complaint import Complaint
from src.models.location import Location
from src.core.constants import SOSStatus, ComplaintStatus


class AnalyticsService:
    @staticmethod
    def get_dashboard_metrics() -> Dict:
        total_users = User.query.count()
        total_complaints = Complaint.query.count()
        total_sos = SOS.query.count()
        active_sos = SOS.query.filter_by(status=SOSStatus.ACTIVE.value).count()

        pending_complaints = Complaint.query.filter_by(
            status=ComplaintStatus.PENDING.value
        ).count()

        return {
            "total_users": total_users,
            "total_complaints": total_complaints,
            "total_sos": total_sos,
            "active_sos": active_sos,
            "pending_complaints": pending_complaints,
        }

    @staticmethod
    def get_sos_trends(days: int = 7) -> List[Dict]:
        start_date = datetime.utcnow() - timedelta(days=days)

        sos_by_day = (
            db.session.query(
                func.date(SOS.start_time).label("date"),
                func.count(SOS.id).label("count"),
            )
            .filter(SOS.start_time >= start_date)
            .group_by(func.date(SOS.start_time))
            .all()
        )

        return [{"date": str(date), "count": count} for date, count in sos_by_day]

    @staticmethod
    def get_complaint_trends(days: int = 7) -> List[Dict]:
        start_date = datetime.utcnow() - timedelta(days=days)

        complaints_by_day = (
            db.session.query(
                func.date(Complaint.timestamp).label("date"),
                func.count(Complaint.id).label("count"),
            )
            .filter(Complaint.timestamp >= start_date)
            .group_by(func.date(Complaint.timestamp))
            .all()
        )

        return [
            {"date": str(date), "count": count} for date, count in complaints_by_day
        ]

    @staticmethod
    def get_complaint_status_distribution() -> Dict:
        status_counts = (
            db.session.query(Complaint.status, func.count(Complaint.id))
            .group_by(Complaint.status)
            .all()
        )

        return {status: count for status, count in status_counts}

    @staticmethod
    def get_user_activity(user_id: int) -> Dict:
        user = User.query.get(user_id)
        if not user:
            return {}

        complaints_count = Complaint.query.filter_by(user_id=user_id).count()
        sos_count = SOS.query.filter_by(user_id=user_id).count()
        active_sos_count = SOS.query.filter_by(
            user_id=user_id, status=SOSStatus.ACTIVE.value
        ).count()

        latest_complaint = (
            Complaint.query.filter_by(user_id=user_id)
            .order_by(Complaint.timestamp.desc())
            .first()
        )
        latest_sos = (
            SOS.query.filter_by(user_id=user_id).order_by(SOS.start_time.desc()).first()
        )

        return {
            "user": user.to_dict(),
            "complaints_count": complaints_count,
            "sos_count": sos_count,
            "active_sos_count": active_sos_count,
            "latest_complaint": (
                latest_complaint.to_dict() if latest_complaint else None
            ),
            "latest_sos": latest_sos.to_dict() if latest_sos else None,
        }

    @staticmethod
    def get_recent_activities(limit: int = 10) -> List[Dict]:
        recent_sos = SOS.query.order_by(SOS.start_time.desc()).limit(limit).all()
        recent_complaints = (
            Complaint.query.order_by(Complaint.timestamp.desc()).limit(limit).all()
        )

        activities = []

        for sos in recent_sos:
            activities.append(
                {
                    "type": "sos",
                    "timestamp": sos.start_time,
                    "data": sos.to_dict(),
                    "user": sos.user.to_dict(),
                }
            )

        for complaint in recent_complaints:
            activities.append(
                {
                    "type": "complaint",
                    "timestamp": complaint.timestamp,
                    "data": complaint.to_dict(),
                    "user": complaint.user.to_dict(),
                }
            )

        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]
