"""
how_long_ago.py

This module provides a function to calculate how much time has passed since (or until) a given datetime.

It supports input as a datetime object or a string, and can return the result in seconds, minutes,
hours, days, months, or years. It is designed so that:

- Past times return positive values (e.g., "10 minutes ago" → 10.0)
- Future times return negative values (e.g., "in 10 minutes" → -10.0)

Use this for logging, reporting, or time-based logic such as "has it been more than X days?".


if __name__ == "__main__":
    print("10 minutes ago:", get(datetime.now().replace(microsecond=0) - timedelta(minutes=10), 'm'), "minutes")
    print("2 days ago:", get(datetime.now() - timedelta(days=2), 'd'), "days")
    print("1 month ago:", get(datetime.now() - relativedelta(months=1), 'mo'), "months")
    print("Future event:", get(datetime.now() + timedelta(hours=5), 'h'), "hours")


"""

from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

def get(target_time, unit: str = 's', date_format: str = "%Y %m %d %H %M %S") -> float:
    if isinstance(target_time, str):
        try:
            target_time = datetime.strptime(target_time, date_format)
        except ValueError:
            target_time = parser.parse(target_time)

    now = datetime.now()
    delta = now - target_time  # Past = positive, future = negative

    if unit == 's':
        return float(delta.total_seconds())
    elif unit == 'm':
        return float(delta.total_seconds() / 60)
    elif unit == 'h':
        return float(delta.total_seconds() / 3600)
    elif unit == 'd':
        return float(delta.total_seconds() / (3600 * 24))
    elif unit in ('mo', 'y'):
        rd = relativedelta(now, target_time)
        months = rd.years * 12 + rd.months + rd.days / 30
        return float(months) if unit == 'mo' else float(months) / 12
    else:
        raise ValueError("Invalid unit. Choose from 's', 'm', 'h', 'd', 'mo', 'y'.")
