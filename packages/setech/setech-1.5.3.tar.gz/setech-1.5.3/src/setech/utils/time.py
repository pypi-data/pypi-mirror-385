import datetime
import zoneinfo

__all__ = ["time_now", "time_utc_now"]


def time_now(timezone: str = "UTC") -> datetime.datetime:
    return datetime.datetime.now(zoneinfo.ZoneInfo(timezone))


def time_utc_now() -> datetime.datetime:
    return time_now("UTC")
