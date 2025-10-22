from __future__ import annotations
from typing import Union, Literal
import datetime as dt

from relationalai.semantics.internal import internal as b
from .std import _DateTime, _Date, _Integer, _String, _make_expr
from .. import std

# TODO support DateTime below as well, but this needs e.g. Rel `datetime_year`

def year(date: _Date) -> b.Expression:
    return _make_expr("date_year", date, b.Int64.ref("res"))

def month(date: _Date) -> b.Expression:
    return _make_expr("date_month", date, b.Int64.ref("res"))

def week(date: _Date) -> b.Expression:
    return _make_expr("date_week", date, b.Int64.ref("res"))

def day(date: _Date) -> b.Expression:
    return _make_expr("date_day", date, b.Int64.ref("res"))

def dates_period_days(start: _Date, end: _Date) -> b.Expression:
    return _make_expr("dates_period_days", start, end, b.Int64.ref("res"))

def datetime_week(datetime: _DateTime, tz: dt.tzinfo|str|None = None) -> b.Expression:
    tz = _extract_tz(datetime, tz)
    return _make_expr("datetime_week", datetime, tz, b.Int64.ref("res"))

def datetimes_period_milliseconds(start: _DateTime, end: _DateTime) -> b.Expression:
    return _make_expr("datetimes_period_milliseconds", start, end, b.Int64.ref("res"))

def date_fromordinal(ordinal: _Integer) -> b.Expression:
    # ordinal 1 = '0001-01-01'. Minus 1 day since we can't declare date 0000-00-00
    return date_add(b.Date(dt.date(1, 1, 1)), days(ordinal - 1))

def datetime_fromordinal(ordinal: _Integer) -> b.Expression:
    # Convert ordinal to milliseconds, since ordinals in Python are days
    # Minus 1 day since we can't declare date 0000-00-00
    ordinal_milliseconds = (ordinal - 1) * 86400000 # 24 * 60 * 60 * 1000
    return datetime_add(b.DateTime(dt.datetime(1, 1, 1, 0, 0, 0)), milliseconds(ordinal_milliseconds))

#--------------------------------------------------
# Periods
#--------------------------------------------------
def milliseconds(period: _Integer) -> b.Expression:
    return _make_expr("millisecond", std.cast_to_int64(period), b.Int64.ref("res"))

def seconds(period: _Integer) -> b.Expression:
    return _make_expr("second", std.cast_to_int64(period), b.Int64.ref("res"))

def minutes(period: _Integer) -> b.Expression:
    return _make_expr("minute", std.cast_to_int64(period), b.Int64.ref("res"))

def hours(period: _Integer) -> b.Expression:
    return _make_expr("hour", std.cast_to_int64(period), b.Int64.ref("res"))

def days(period: _Integer) -> b.Expression:
    return _make_expr("day", std.cast_to_int64(period), b.Int64.ref("res"))

def weeks(period: _Integer) -> b.Expression:
    return _make_expr("week", std.cast_to_int64(period), b.Int64.ref("res"))

def months(period: _Integer) -> b.Expression:
    return _make_expr("month", std.cast_to_int64(period), b.Int64.ref("res"))

def years(period: _Integer) -> b.Expression:
    return _make_expr("year", std.cast_to_int64(period), b.Int64.ref("res"))

def date_to_datetime(date: _Date, hour: int = 0, minute: int = 0, second: int = 0, millisecond: int = 0, tz: str = "UTC") -> b.Expression:
    _year = year(date)
    _month = month(date)
    _day = day(date)
    return _make_expr("construct_datetime_ms_tz", _year, _month, _day, hour, minute, second, millisecond, tz, b.DateTime.ref("res"))

def datetime_to_date(datetime: _DateTime, tz: dt.tzinfo | str | None = None) -> b.Expression:
    tz = _extract_tz(datetime, tz)
    return _make_expr("construct_date_from_datetime", datetime, tz, b.Date.ref("res"))

#--------------------------------------------------
# String Formatting
#--------------------------------------------------

def date_format(date: _Date, format: _String) -> b.Expression:
    return _make_expr("date_format", date, format, b.String.ref("res"))

def datetime_format(date: _DateTime, format: _String, tz: _String = "UTC") -> b.Expression:
    return _make_expr("datetime_format", date, format, tz, b.String.ref("res"))

#--------------------------------------------------
# Arithmetic
#--------------------------------------------------
def date_add(date: _Date, period: b.Producer) -> b.Expression:
    return _make_expr("date_add", date, period, b.Date.ref("res"))

def date_subtract(date: _Date, period: b.Producer) -> b.Expression:
    return _make_expr("date_subtract", date, period, b.Date.ref("res"))

def datetime_add(date: _DateTime, period: b.Producer) -> b.Expression:
    return _make_expr("datetime_add", date, period, b.DateTime.ref("res"))

def datetime_subtract(date: _DateTime, period: b.Producer) -> b.Expression:
    return _make_expr("datetime_subtract", date, period, b.DateTime.ref("res"))


Frequency = Union[
    Literal["ms"],
    Literal["s"],
    Literal["m"],
    Literal["H"],
    Literal["D"],
    Literal["W"],
    Literal["M"],
    Literal["Y"],
]

_periods = {
    "ms": milliseconds,
    "s": seconds,
    "m": minutes,
    "H": hours,
    "D": days,
    "W": weeks,
    "M": months,
    "Y": years,
}

# Note on date_ranges and datetime_range: The way the computation works is that it first overapproximates the number of periods.
# For example date_range(2025-02-01, 2025-03-01, freq='M') and date_range(2025-02-01, 2025-03-31, freq='M') will compute
# range_end to be ceil(28*1/(365/12))=1 and ceil(58*1/(365/12))=2. Then, the computation fetches range_end+1 items into _date, which
# is the right number in the first case but one too many in the second case. That's why a filter end >= _date (or variant of) is
# applied, to remove any extra item. The result is two items in both cases.

def date_range(start: _Date | None = None, end: _Date | None = None, periods: int = 1, freq: Frequency = "D") -> b.Expression:
    if start is None and end is None:
        raise ValueError("Invalid start/end date for date_range. Must provide at least start date or end date")
    _days = {
        "D": 1,
        "W": 1/7,
        "M": 1/(365/12),
        "Y": 1/365,
    }
    if freq not in _days.keys():
        raise ValueError(f"Frequency '{freq}' is not allowed for date_range. List of allowed frequencies: {list(_days.keys())}")
    date_func = date_add
    if start is None:
        start = end
        end = None
        date_func = date_subtract
    assert start is not None
    if end is not None:
        num_days = std.dates.dates_period_days(start, end)
        if freq in ["W", "M", "Y"]:
            range_end = std.cast(b.Int64, std.math.ceil(num_days * _days[freq]))
        else:
            range_end = num_days
        # date_range is inclusive. add 1 since std.range is exclusive
        ix = std.range(0, range_end + 1, 1)
    else:
        ix = std.range(0, periods, 1)
    _date = date_func(start, _periods[freq](ix))
    if isinstance(end, dt.date) :
        return b.Date(end) >= _date
    elif end is not None:
        return end >= _date
    return _date

def datetime_range(start: _DateTime | None = None, end: _DateTime | None = None, periods: int = 1, freq: Frequency = "D") -> b.Expression:
    if start is None and end is None:
        raise ValueError("Invalid start/end datetime for datetime_range. Must provide at least start datetime or end datetime")
    _milliseconds = {
        "ms": 1,
        "s": 1 / 1_000,
        "m": 1 / 60_000,
        "H": 1 / 3_600_000,
        "D": 1 / 86_400_000,
        "W": 1 / (86_400_000 * 7),
        "M": 1 / (86_400_000 * (365 / 12)),
        "Y": 1 / (86_400_000 * 365),
    }
    date_func = datetime_add
    if start is None:
        start = end
        end = None
        date_func = datetime_subtract
    assert start is not None
    if end is not None:
        num_ms = datetimes_period_milliseconds(start, end)
        if freq == "ms":
            _end = num_ms
        else:
            _end = std.cast(b.Int64, std.math.ceil(num_ms * _milliseconds[freq]))
        # datetime_range is inclusive. add 1 since std.range is exclusive
        ix = std.range(0, _end + 1, 1)
    else:
        ix = std.range(0, periods, 1)
    _date = date_func(start, _periods[freq](ix))
    if isinstance(end, dt.datetime) :
        return b.DateTime(end) >= _date
    elif end is not None:
        return end >= _date
    return _date

def _extract_tz(datetime: _DateTime, tz: dt.tzinfo|str|None) -> str:
    default_tz = "UTC"
    if tz is None:
        if isinstance(datetime, dt.datetime):
            tz = datetime.tzname() or default_tz
        else:
            tz = default_tz
    elif isinstance(tz, dt.tzinfo) :
        tz = tz.tzname(None) or default_tz
    return tz
