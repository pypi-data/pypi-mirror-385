"""
This module contains logic for casting string values to native python types.

Except for :func:`str2bool` and :func:`str2timedelta`, these are mostly just thin wrappers around built-in methods,
and only provided for convenience.
"""

from datetime import date, datetime, time, timedelta
from json import JSONDecodeError, loads
from pathlib import Path
from re import compile
from typing import Any
from urllib.parse import ParseResult, urlparse


def str2bool(value: str) -> bool:
    """
    Parse a string into a boolean value.

    The function recognizes the following strings, case insensitively:

    =======  =======
    True     False
    =======  =======
    "True"   "False"
    "T"      "F"
    "1"      "0"
    "Yes"    "No"
    "Y"      "N"
    =======  =======

    :param value: The boolean string value to parse.
    :raise ValueError: If the string is not a valid (recognized) boolean value.
    :return: The boolean value based on the string content.
    """
    # Normalize the value to lowercase and compare with various possible representations of True and False
    truthy_values = {"true", "t", "1", "yes", "y"}
    falsy_values = {"false", "f", "0", "no", "n"}

    # Normalize input (remove extra spaces and make lowercase)
    value = value.strip().lower()

    if value in truthy_values:
        return True
    elif value in falsy_values:
        return False
    else:
        raise ValueError(f'Invalid boolean value for "{value}". '
                         f'Expected one of: {", ".join(truthy_values)} or {", ".join(falsy_values)}.')


def str2int(value: str) -> int:
    """
    Parse a string into an integer value.

    This is just an alias for ``int``.

    :param value: The integer string value to parse.
    :raise ValueError: If the string cannot be converted to an integer.
    :return: The parsed integer value.
    """
    return int(value.strip())


def str2float(value: str) -> float:
    """
    Parse a string into a float value.

    This is just an alias for ``float``.

    :param value: The float string value to parse.
    :raise ValueError: If the string cannot be converted to a float.
    :return: The parsed float value.
    """
    return float(value.strip())


def str2date(value: str) -> date:
    """
    Parse a string into a date value using ISO format.

    This is just an alias for ``datetime.date.fromisoformat``.

    :param value: The date string in ISO format (YYYY-MM-DD).
    :raise ValueError: If the string is not a valid ISO date format.
    :return: The parsed date object.
    """
    return date.fromisoformat(value.strip())


def str2datetime(value: str) -> datetime:
    """
    Parse a string into a datetime value using ISO format.

    This is just an alias for ``datetime.datetime.fromisoformat``.

    :param value: The datetime string in ISO format (YYYY-MM-DDTHH:MM:SS).
    :raise ValueError: If the string is not a valid ISO datetime format.
    :return: The parsed datetime object.
    """
    return datetime.fromisoformat(value.strip())


def str2time(value: str) -> time:
    """
    Parse a string into a time value using ISO format.

    This is just an alias for ``datetime.time.fromisoformat``.

    :param value: The time string in ISO format (HH:MM:SS).
    :raise ValueError: If the string is not a valid ISO time format.
    :return: The parsed time object.
    """
    return time.fromisoformat(value.strip())


def str2timedelta(value: str) -> timedelta:
    """
    Parse a string into a timedelta.

    Supports formats like:

    - "5d" (5 days)
    - "2h" (2 hours)
    - "30m" (30 minutes)
    - "45s" (45 seconds)
    - "1d 2h 30m" (combinations)

    :param value: The timedelta string to parse.
    :raise ValueError: If the string format is not recognized.
    :return: The parsed timedelta object.
    """
    value = value.strip().lower()

    # Pattern to match time components in order (d, h, m, s)
    pattern = compile(r"(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?")
    match = pattern.fullmatch(value)

    # Require a full-string match and at least one time component present
    if not match or not any(match.groups()):
        raise ValueError(
            f'Invalid timedelta format: "{value}". '
            'Expected format like "5d", "2h", "30m", "45s" or combinations.'
        )

    days, hours, minutes, seconds = match.groups()

    # Convert to integers, defaulting to 0 if not present
    days = int(days) if days else 0
    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds) if seconds else 0

    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def str2path(value: str) -> Path:
    """
    Parse a string into a Path object.

    The path will be expanded (~ becomes home directory) and resolved to an absolute path.

    :param value: The path string to parse.
    :return: The parsed Path object.
    """
    return Path(value.strip()).expanduser().resolve()


def str2url(value: str) -> ParseResult:
    """
    Parse a string into a URL ParseResult object.

    This is just an alias for ``urllib.parse.urlparse``.

    :param value: The URL string to parse.
    :return: The parsed URL as a ParseResult object.
    """
    return urlparse(value.strip())


def str2json(value: str) -> dict[str, Any]:
    """
    Parse a JSON string into a Python object.

    This is just an alias for ``json.loads``.

    :param value: The JSON string to parse.
    :raise ValueError: If the string is not valid JSON.
    :return: The parsed Python object (dict, list, str, int, float, bool, or None).
    """
    try:
        return loads(value.strip())
    except JSONDecodeError as e:
        raise ValueError(f'Invalid JSON string: "{value}".') from e
