from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from src.core.extensions import db
from src.models.location import Location
from src.models.user import User


class LocationService:
    @staticmethod
    def add_location(
        user_id: int,
        latitude: float,
        longitude: float,
        accuracy: Optional[float] = None,
        update_type: str = "manual",
        sos_id: Optional[int] = None,
    ) -> Tuple[bool, str, Optional[Location]]:
        location = Location(
            user_id=user_id,
            sos_id=sos_id,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            update_type=update_type,
        )

        try:
            db.session.add(location)
            db.session.commit()
            return True, "Location added", location
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to add location: {str(e)}", None

    @staticmethod
    def get_user_locations(user_id: int, limit: int = 100) -> List[Location]:
        return (
            Location.query.filter_by(user_id=user_id)
            .order_by(Location.timestamp.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_latest_location(user_id: int) -> Optional[Location]:
        return (
            Location.query.filter_by(user_id=user_id)
            .order_by(Location.timestamp.desc())
            .first()
        )

    @staticmethod
    def get_sos_locations(sos_id: int) -> List[Location]:
        return (
            Location.query.filter_by(sos_id=sos_id)
            .order_by(Location.timestamp.asc())
            .all()
        )

    @staticmethod
    def get_recent_locations(hours: int = 24) -> List[Location]:
        since = datetime.utcnow() - timedelta(hours=hours)
        return (
            Location.query.filter(Location.timestamp >= since)
            .order_by(Location.timestamp.desc())
            .all()
        )

    @staticmethod
    def get_all_active_user_locations() -> List[dict]:
        from src.core.constants import SOSStatus
        from src.models.sos import SOS

        active_sos_users = (
            db.session.query(SOS.user_id).filter_by(status=SOSStatus.ACTIVE.value).all()
        )
        active_user_ids = [user_id for (user_id,) in active_sos_users]

        locations = []
        for user_id in active_user_ids:
            latest = LocationService.get_user_latest_location(user_id)
            if latest:
                user = User.query.get(user_id)
                locations.append(
                    {
                        "user_id": user_id,
                        "user_name": user.name if user else "Unknown",
                        "location": latest.to_dict(),
                    }
                )

        return locations

    @staticmethod
    def get_heatmap_data(hours: int = 24) -> List[Tuple[float, float]]:
        locations = LocationService.get_recent_locations(hours)
        return [(loc.latitude, loc.longitude) for loc in locations]
