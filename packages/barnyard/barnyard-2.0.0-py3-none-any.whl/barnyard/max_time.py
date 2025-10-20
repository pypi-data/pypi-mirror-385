#import max_time



"""
Timestamp Utilities Module
--------------------------

This module provides flexible utilities for working with date and time values in Python.

Functions:
1. now():
   - Generates the current timestamp with flexible output options.
   - Supports returning datetime, date, time, or individual components (day, hour, minute, second).
   - Allows timezone-aware timestamps by specifying a timezone string.
   - Can output as a formatted string, raw datetime object, or Unix timestamp integer.
   - Designed to simplify obtaining "now" in different forms without repeated boilerplate.

2. auto_changetype(value):
   - Converts between string and datetime seamlessly.
   - If input is a string, attempts to parse it into a datetime object (using dateutil.parser).
   - If input is a datetime, converts it to a standard formatted string.
   - Always strips microseconds for consistency.
   - Useful for flexible input/output handling where date/time values may come as strings or datetime objects.

Thought Process and Design:
- The `now()` function is created to unify common timestamp-related operations in one place.
- Instead of multiple functions for each timestamp type, a single interface uses the `stamp` parameter to specify desired output.
- Support for timezone conversion addresses the common need to work with multiple timezones.
- The option to return Unix timestamps or formatted strings increases the function's versatility.
- `auto_changetype()` abstracts parsing and formatting logic to easily toggle between string and datetime representations.
- This avoids repetitive parsing and formatting code throughout an application, promoting DRY (Don't Repeat Yourself) principles.
- Both functions explicitly remove microseconds to avoid subtle bugs or mismatches when microsecond precision is unnecessary or undesired.


# Get current datetime object (local timezone)
dt = now()

# Get current time as string in default format
t_str = now(stamp='time', as_string=True)

# Get Unix timestamp for now in UTC
unix_utc = now(unix=True, tz='UTC')

# Parse string to datetime object
dt_parsed = auto_changetype("2025-05-25 15:30:00")

# Convert datetime object back to formatted string
dt_str = auto_changetype(datetime.now())

"""






from datetime import datetime, timedelta
import pytz

def now(
    as_string: bool = False,
    stamp: str = "datetime",  # Options: datetime, date, time, d, h, m, s
    tz: str = None,
    fmt: str = "%Y-%m-%d %H:%M:%S",
    unix: bool = False,
):
    """
    A flexible timestamp generator.

    Parameters:
        stamp (str): 'datetime' (default), 'date', 'time', or shortcuts:
                     'd' (days), 'h' (hours), 'm' (minutes), 's' (seconds)
        as_string (bool): Return as string using `fmt`.
        tz (str): Timezone name (e.g., 'UTC', 'Asia/Kolkata').
        fmt (str): Format string for strftime (used if as_string=True).
        unix (bool): If True, return Unix timestamp (int).

    Returns:
        datetime, str, int, or float: Depending on options selected.
    """
    stamp = stamp.lower()
    now = datetime.now()

    # Apply timezone if provided
    if tz:
        try:
            now = now.astimezone(pytz.timezone(tz))
        except pytz.UnknownTimeZoneError:
            raise ValueError(f"Invalid timezone: {tz}")

    # Strip microseconds
    now = now.replace(microsecond=0)

    # Return Unix timestamp
    if unix:
        return int(now.timestamp())

    # Return specific part of the datetime
    if stamp in ("date",):
        return now.strftime("%Y-%m-%d") if as_string else now.date()
    elif stamp in ("time",):
        return now.strftime("%H:%M:%S") if as_string else now.time()
    elif stamp in ("datetime",):
        return now.strftime(fmt) if as_string else now
    elif stamp == "s":
        return now.second
    elif stamp == "m":
        return now.minute
    elif stamp == "h":
        return now.hour
    elif stamp == "d":
        return now.day
    else:
        raise ValueError(f"Invalid value for 'stamp': {stamp}")




from datetime import datetime
from dateutil import parser

def auto_changetype(value):
    """
    Converts between string and datetime, parsing with dateutil.parser.

    - If input is a string: returns datetime_object (no tuple)
    - If input is a datetime: returns formatted string using ISO-style format
    - Always removes microseconds.
    """
    if isinstance(value, str):
        try:
            dt = parser.parse(value).replace(microsecond=0)
            return dt  # Return just the datetime object
        except Exception as e:
            raise ValueError(f"Could not parse string: {value}") from e

    elif isinstance(value, datetime):
        return value.replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

    else:
        raise TypeError("Input must be a string or datetime object")




