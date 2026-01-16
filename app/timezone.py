"""
Taiwan Timezone Utilities
"""
from datetime import datetime, timezone, timedelta

# Taiwan timezone (UTC+8)
TW_TIMEZONE = timezone(timedelta(hours=8))


def now_tw():
    """Get current datetime in Taiwan timezone"""
    return datetime.now(TW_TIMEZONE)


def today_tw():
    """Get current date in Taiwan timezone"""
    return now_tw().date()


def to_tw_time(dt):
    """Convert a datetime to Taiwan timezone"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TW_TIMEZONE)
