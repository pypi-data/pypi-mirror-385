"""
Helper module for date formats.
"""

import datetime


def today() -> str:
    """
    Returns todays date in the correct iso format.
    """
    return datetime.date.isoformat(datetime.date.today())


def is_iso8601(date: str) -> bool:
    """
    Validates that the given date is in the ISO 8601 format (https://en.wikipedia.org/wiki/ISO_8601)
    """
    try:
        datetime.datetime.fromisoformat(date)
        return True
    except ValueError:
        return False
