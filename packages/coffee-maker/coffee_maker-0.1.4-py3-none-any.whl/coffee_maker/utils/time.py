"""Time utilities for analytics and reporting.

This module provides reusable time calculation functions to reduce code
duplication across analytics modules.

Example:
    >>> from coffee_maker.utils.time import get_time_threshold, format_duration
    >>>
    >>> # Get time threshold for "last 7 days"
    >>> from_time = get_time_threshold("day", count=7)
    >>>
    >>> # Format duration
    >>> formatted = format_duration(3665)  # "1h 1m 5s"
"""

import time
from datetime import datetime, timedelta
from typing import Optional, Tuple

# Time constants (in seconds)
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = 86400
SECONDS_IN_WEEK = 604800


def get_time_threshold(
    timeframe: str,
    count: int = 1,
    reference_time: Optional[datetime] = None,
) -> datetime:
    """Get time threshold for a timeframe string.

    Args:
        timeframe: Timeframe unit ("minute", "hour", "day", "week", "month", "all")
        count: Number of units to go back (default: 1)
        reference_time: Reference time to calculate from (default: now)

    Returns:
        datetime representing the threshold

    Raises:
        ValueError: If timeframe is invalid

    Example:
        >>> # Last 24 hours
        >>> from_time = get_time_threshold("day")
        >>>
        >>> # Last 7 days
        >>> from_time = get_time_threshold("day", count=7)
        >>>
        >>> # Last 3 months
        >>> from_time = get_time_threshold("month", count=3)
    """
    now = reference_time or datetime.utcnow()

    # Special case: all time
    if timeframe == "all":
        return datetime.min

    # Timeframe to timedelta mapping
    thresholds = {
        "second": timedelta(seconds=count),
        "minute": timedelta(minutes=count),
        "hour": timedelta(hours=count),
        "day": timedelta(days=count),
        "week": timedelta(weeks=count),
        "month": timedelta(days=30 * count),  # Approximate
        "year": timedelta(days=365 * count),  # Approximate
    }

    delta = thresholds.get(timeframe)
    if delta is None:
        valid_options = list(thresholds.keys()) + ["all"]
        raise ValueError(f"Invalid timeframe: {timeframe}. Valid options: {valid_options}")

    return now - delta


def get_time_range(
    timeframe: str,
    count: int = 1,
    reference_time: Optional[datetime] = None,
) -> Tuple[datetime, datetime]:
    """Get time range (from, to) for a timeframe.

    Args:
        timeframe: Timeframe unit
        count: Number of units
        reference_time: Reference time (default: now)

    Returns:
        Tuple of (from_time, to_time)

    Example:
        >>> from_time, to_time = get_time_range("day", count=7)
        >>> # Returns (7 days ago, now)
    """
    to_time = reference_time or datetime.utcnow()
    from_time = get_time_threshold(timeframe, count, reference_time=to_time)
    return from_time, to_time


def format_duration(seconds: float, precision: int = 2) -> str:
    """Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds
        precision: Number of units to show (default: 2)

    Returns:
        Formatted string (e.g., "1h 23m", "45s", "2d 3h")

    Example:
        >>> format_duration(3665)
        '1h 1m'
        >>> format_duration(3665, precision=3)
        '1h 1m 5s'
        >>> format_duration(90)
        '1m 30s'
    """
    if seconds < 0:
        return "0s"

    units = [
        ("d", 86400),  # days
        ("h", 3600),  # hours
        ("m", 60),  # minutes
        ("s", 1),  # seconds
    ]

    parts = []
    remaining = seconds

    for unit_name, unit_seconds in units:
        if remaining >= unit_seconds:
            value = int(remaining // unit_seconds)
            parts.append(f"{value}{unit_name}")
            remaining %= unit_seconds

        if len(parts) >= precision:
            break

    return " ".join(parts) if parts else "0s"


def format_timestamp(
    dt: datetime,
    format: str = "iso",
    timezone_aware: bool = False,
) -> str:
    """Format datetime to string.

    Args:
        dt: Datetime to format
        format: Format type ("iso", "human", "compact")
        timezone_aware: Whether to include timezone info

    Returns:
        Formatted timestamp string

    Example:
        >>> now = datetime.utcnow()
        >>> format_timestamp(now, "iso")
        '2025-01-09T12:34:56'
        >>> format_timestamp(now, "human")
        'January 09, 2025 12:34 PM'
        >>> format_timestamp(now, "compact")
        '2025-01-09_12-34-56'
    """
    if format == "iso":
        result = dt.isoformat()
    elif format == "human":
        result = dt.strftime("%B %d, %Y %I:%M %p")
    elif format == "compact":
        result = dt.strftime("%Y-%m-%d_%H-%M-%S")
    elif format == "date_only":
        result = dt.strftime("%Y-%m-%d")
    elif format == "time_only":
        result = dt.strftime("%H:%M:%S")
    else:
        raise ValueError(f"Invalid format: {format}")

    if timezone_aware and format == "iso":
        # Add UTC indicator if not already present
        if not result.endswith("Z") and "+" not in result:
            result += "Z"

    return result


def bucket_time(
    dt: datetime,
    bucket_size_hours: int = 24,
) -> datetime:
    """Bucket a datetime into time buckets.

    Useful for aggregating data by time periods (hourly, daily, etc.).

    Args:
        dt: Datetime to bucket
        bucket_size_hours: Bucket size in hours (default: 24 for daily)

    Returns:
        Bucketed datetime (truncated to bucket boundary)

    Example:
        >>> # Daily buckets
        >>> dt = datetime(2025, 1, 9, 15, 30, 0)
        >>> bucket_time(dt, bucket_size_hours=24)
        datetime(2025, 1, 9, 0, 0, 0)
        >>>
        >>> # Hourly buckets
        >>> bucket_time(dt, bucket_size_hours=1)
        datetime(2025, 1, 9, 15, 0, 0)
    """
    # Round down to bucket boundary
    # Use UTC epoch to avoid timezone issues
    epoch = datetime(1970, 1, 1)
    hours_since_epoch = int((dt - epoch).total_seconds() / 3600)
    bucket_hours = (hours_since_epoch // bucket_size_hours) * bucket_size_hours
    return epoch + timedelta(hours=bucket_hours)


def is_recent(
    dt: datetime,
    threshold_seconds: float = 60,
    reference_time: Optional[datetime] = None,
) -> bool:
    """Check if a datetime is recent (within threshold).

    Args:
        dt: Datetime to check
        threshold_seconds: How many seconds ago is "recent"
        reference_time: Reference time (default: now)

    Returns:
        True if datetime is within threshold

    Example:
        >>> now = datetime.utcnow()
        >>> recent_dt = now - timedelta(seconds=30)
        >>> is_recent(recent_dt, threshold_seconds=60)
        True
        >>> old_dt = now - timedelta(minutes=5)
        >>> is_recent(old_dt, threshold_seconds=60)
        False
    """
    now = reference_time or datetime.utcnow()
    age_seconds = (now - dt).total_seconds()
    # Only consider past datetimes as recent (age >= 0)
    return 0 <= age_seconds <= threshold_seconds


def time_ago(
    dt: datetime,
    reference_time: Optional[datetime] = None,
) -> str:
    """Format datetime as "X ago" string.

    Args:
        dt: Datetime to format
        reference_time: Reference time (default: now)

    Returns:
        Human-readable "ago" string

    Example:
        >>> now = datetime.utcnow()
        >>> dt = now - timedelta(minutes=5)
        >>> time_ago(dt)
        '5 minutes ago'
        >>> dt = now - timedelta(hours=2)
        >>> time_ago(dt)
        '2 hours ago'
    """
    now = reference_time or datetime.utcnow()
    delta = now - dt

    seconds = delta.total_seconds()

    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:  # 7 days
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:  # 30 days
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"


def get_timestamp_threshold(
    timeframe: str,
    reference_time: Optional[float] = None,
) -> float:
    """Get Unix timestamp threshold for a timeframe.

    Useful for filtering data by time periods using Unix timestamps.
    Eliminates duplicate time threshold calculation across modules.

    Args:
        timeframe: One of "minute", "hour", "day", or "all"
        reference_time: Reference Unix timestamp (default: current time)

    Returns:
        Unix timestamp threshold

    Raises:
        ValueError: If timeframe is invalid

    Example:
        >>> # Get threshold for last day
        >>> threshold = get_timestamp_threshold("day")
        >>> # Returns timestamp from 24 hours ago
        >>>
        >>> # Get threshold for last hour
        >>> threshold = get_timestamp_threshold("hour")
        >>> # Returns timestamp from 1 hour ago
        >>>
        >>> # Get all data
        >>> threshold = get_timestamp_threshold("all")
        >>> # Returns 0 (Unix epoch)
    """
    if reference_time is None:
        reference_time = time.time()

    # Special case: all time
    if timeframe == "all":
        return 0

    # Timeframe to seconds mapping
    timeframe_map = {
        "minute": SECONDS_IN_MINUTE,
        "hour": SECONDS_IN_HOUR,
        "day": SECONDS_IN_DAY,
    }

    offset = timeframe_map.get(timeframe)
    if offset is None:
        valid_options = list(timeframe_map.keys()) + ["all"]
        raise ValueError(f"Invalid timeframe: {timeframe}. Valid options: {valid_options}")

    return reference_time - offset
