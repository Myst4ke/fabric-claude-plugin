#!/usr/bin/env python3
"""Shared helpers for Fabric job schedule configurations.

The Fabric scheduler API does NOT accept unix cron expressions. A schedule
configuration is one of:
  {"type": "Cron",   "interval": <minutes>, ...}
  {"type": "Daily",  "times": ["HH:mm", ...], ...}
  {"type": "Weekly", "weekdays": ["Monday", ...], "times": ["HH:mm", ...], ...}
plus startDateTime, endDateTime and localTimeZoneId on every type.
"""

from datetime import datetime, timedelta, timezone

_WEEKDAYS = {
    'mon': 'Monday', 'tue': 'Tuesday', 'wed': 'Wednesday', 'thu': 'Thursday',
    'fri': 'Friday', 'sat': 'Saturday', 'sun': 'Sunday',
}


def normalize_weekday(day):
    full = _WEEKDAYS.get(day.strip().lower()[:3])
    if not full or (len(day.strip()) > 3 and full.lower() != day.strip().lower()):
        raise ValueError(f"Invalid weekday: {day}")
    return full


def validate_time(t):
    parts = t.split(':')
    if len(parts) != 2 or not all(p.isdigit() for p in parts) \
            or not (0 <= int(parts[0]) <= 23 and 0 <= int(parts[1]) <= 59):
        raise ValueError(f"Invalid time (expected HH:MM): {t}")
    return f"{int(parts[0]):02d}:{int(parts[1]):02d}"


def default_window():
    start = datetime.now(timezone.utc)
    end = start + timedelta(days=365 * 5)
    fmt = "%Y-%m-%dT%H:%M:%S"
    return start.strftime(fmt), end.strftime(fmt)


def build_configuration(every=None, daily=None, weekly_days=None, weekly_times=None,
                        start=None, end=None, tz='UTC'):
    """Build a scheduler API configuration from CLI-style options."""
    d_start, d_end = default_window()
    config = {
        'startDateTime': start or d_start,
        'endDateTime': end or d_end,
        'localTimeZoneId': tz,
    }
    if every is not None:
        config['type'] = 'Cron'
        config['interval'] = int(every)
    elif daily:
        config['type'] = 'Daily'
        config['times'] = [validate_time(t) for t in daily]
    elif weekly_days:
        if not weekly_times:
            raise ValueError("Weekly schedules need at least one HH:MM time")
        config['type'] = 'Weekly'
        config['weekdays'] = [normalize_weekday(d) for d in weekly_days]
        config['times'] = [validate_time(t) for t in weekly_times]
    else:
        raise ValueError("One of --every / --daily / --weekly is required")
    return config


def describe(config):
    t = config.get('type')
    if t == 'Cron':
        return f"every {config.get('interval')} minute(s)"
    if t == 'Daily':
        return f"daily at {', '.join(config.get('times', []))}"
    if t == 'Weekly':
        return (f"weekly on {', '.join(config.get('weekdays', []))}"
                f" at {', '.join(config.get('times', []))}")
    return t or 'unknown'
