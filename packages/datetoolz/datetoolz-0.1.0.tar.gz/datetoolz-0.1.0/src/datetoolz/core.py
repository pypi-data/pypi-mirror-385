from __future__ import annotations

from datetime import date, timedelta
from typing import Literal

ISODateString = str

WEEKDAY_NAMES: list[str] = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
]

WEEKDAY_ABBRS: list[str] = [
    "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun",
]

WeekdayFormat = Literal["name", "abbr", "index"]


def _to_iso(d: date) -> ISODateString:
    return d.isoformat()


def today() -> ISODateString:
    """Return today's date as YYYY-MM-DD."""
    return _to_iso(date.today())


def yesterday() -> ISODateString:
    """Return yesterday's date as YYYY-MM-DD."""
    return _to_iso(date.today() - timedelta(days=1))


def tomorrow() -> ISODateString:
    """Return tomorrow's date as YYYY-MM-DD."""
    return _to_iso(date.today() + timedelta(days=1))


def weekday(fmt: WeekdayFormat = "name") -> str | int:
    """Return today's weekday.

    - fmt="name": full name (e.g., "Monday")
    - fmt="abbr": abbreviation (e.g., "Mon")
    - fmt="index": ISO index 1..7 (Mon..Sun)
    """
    idx = date.today().isoweekday()  # 1..7 for Mon..Sun
    if fmt == "index":
        return idx
    if fmt == "abbr":
        return WEEKDAY_ABBRS[idx - 1]
    return WEEKDAY_NAMES[idx - 1]


__all__ = [
    "today",
    "yesterday",
    "tomorrow",
    "weekday",
]
