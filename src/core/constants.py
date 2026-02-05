from enum import Enum


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"


class SOSStatus(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    RESOLVED = "resolved"


class ComplaintStatus(Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    CLOSED = "closed"


class LocationUpdateType(Enum):
    SOS = "sos"
    MANUAL = "manual"
    PERIODIC = "periodic"


SOS_LOCATION_UPDATE_INTERVAL = 10
SESSION_TIMEOUT_DAYS = 30
MAX_LOCATION_HISTORY = 1000
ADMIN_EMAIL_DOMAIN = "admin.pyraksha.org"
