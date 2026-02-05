from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import and_, or_
from src.core.extensions import db
from src.models.sos import SOS
from src.models.location import Location
from src.models.user import User
from src.core.constants import SOSStatus, LocationUpdateType


class SOSService:
    @staticmethod
    def create_sos(
        user_id: int, sos_id: str, initial_location: Optional[dict] = None
    ) -> Tuple[bool, str, Optional[SOS]]:
        active_sos = SOS.query.filter(
            and_(SOS.user_id == user_id, SOS.status == SOSStatus.ACTIVE.value)
        ).first()

        if active_sos:
            return False, "An active SOS already exists for this user", active_sos

        sos = SOS(sos_id=sos_id, user_id=user_id)
        sos.activate()

        try:
            db.session.add(sos)
            db.session.flush()

            if initial_location:
                location = Location.from_dict(initial_location, user_id, sos.id)
                location.update_type = LocationUpdateType.SOS.value
                db.session.add(location)

            db.session.commit()
            return True, "SOS created successfully", sos
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to create SOS: {str(e)}", None

    @staticmethod
    def add_location_update(sos_id: str, location_data: dict) -> Tuple[bool, str]:
        sos = SOS.query.filter_by(sos_id=sos_id).first()
        if not sos:
            return False, "SOS not found"

        if sos.status != SOSStatus.ACTIVE.value:
            return False, "SOS is not active"

        location = Location.from_dict(location_data, sos.user_id, sos.id)
        location.update_type = LocationUpdateType.SOS.value

        try:
            db.session.add(location)
            db.session.commit()
            return True, "Location updated"
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to update location: {str(e)}"

    @staticmethod
    def resolve_sos(
        sos_id: str, resolved_by_id: Optional[int] = None, notes: Optional[str] = None
    ) -> Tuple[bool, str]:
        sos = SOS.query.filter_by(sos_id=sos_id).first()
        if not sos:
            return False, "SOS not found"

        if sos.status == SOSStatus.RESOLVED.value:
            return False, "SOS already resolved"

        sos.resolve(resolved_by_id, notes)

        try:
            db.session.commit()
            return True, "SOS resolved successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to resolve SOS: {str(e)}"

    @staticmethod
    def get_active_sos_events() -> List[SOS]:
        return (
            SOS.query.filter_by(status=SOSStatus.ACTIVE.value)
            .order_by(SOS.start_time.desc())
            .all()
        )

    @staticmethod
    def get_user_sos_history(user_id: int, limit: int = 50) -> List[SOS]:
        return (
            SOS.query.filter_by(user_id=user_id)
            .order_by(SOS.start_time.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_sos_by_id(sos_id: str) -> Optional[SOS]:
        return SOS.query.filter_by(sos_id=sos_id).first()

    @staticmethod
    def get_all_sos_events(status: Optional[str] = None, limit: int = 100) -> List[SOS]:
        query = SOS.query
        if status:
            query = query.filter_by(status=status)
        return query.order_by(SOS.start_time.desc()).limit(limit).all()

    @staticmethod
    def get_sos_statistics() -> dict:
        total = SOS.query.count()
        active = SOS.query.filter_by(status=SOSStatus.ACTIVE.value).count()
        resolved = SOS.query.filter_by(status=SOSStatus.RESOLVED.value).count()

        return {"total": total, "active": active, "resolved": resolved}
