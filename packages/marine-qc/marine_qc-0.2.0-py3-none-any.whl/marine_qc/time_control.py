"""Some generally helpful time control functions for base QC."""

from __future__ import annotations
import calendar
import math
from collections.abc import Callable, Sequence
from datetime import datetime

import numpy as np
import pandas as pd

from .auxiliary import (
    generic_decorator,
    inspect_arrays,
    is_scalar_like,
    isvalid,
    post_format_return_type,
)


def convert_date(params: list[str]) -> Callable:
    """
    Decorator to extract date components and inject them as function parameters.

    This decorator intercepts the 'date' argument from the function call, splits it into
    its components (e.g., year, month, day), and assigns those components to specified
    parameters in the wrapped function. It supports scalar or sequence inputs for 'date'.

    Parameters
    ----------
    params : list of str
        List of parameter names corresponding to date components to be extracted and
        passed to the decorated function.

    Returns
    -------
    Callable
        A decorator that wraps a function, extracting date components before calling it.

    Notes
    -----
    - The decorator expects the wrapped function to accept the parameters listed in
      `params`. If a parameter is missing, it raises a `ValueError`.
    - If the 'date' argument is None, the original function is called without modification.
    - Supports scalar-like 'date' values as well as iterable sequences.
    - Assumes a helper function `split_date` exists that splits a date into components
      and returns a dictionary mapping parameter names to their values.
    """

    def pre_handler(arguments: dict, **meta_kwargs):
        date = arguments.get("date")

        if date is None:
            return

        if is_scalar_like(date):
            scalar = True
            extracted = split_date(date)
        else:
            scalar = False
            extracted = [split_date(d) for d in date]

        for param in params:
            if param not in arguments:
                raise ValueError(f"Parameter '{param}' is not a valid parameter.")

            if scalar:
                value = extracted[param]
            else:
                value = [e[param] for e in extracted]

            arguments[param] = value

    pre_handler._decorator_kwargs = set()

    return generic_decorator(pre_handler=pre_handler)


def split_date(date: datetime) -> dict:
    """
    Split datetime date into year, month, day and hour.

    Parameters
    ----------
    date: datetime
        Date to split

    Returns
    -------
    dict
        Dictionary containing year, month, day and hour.
    """
    try:
        date = pd.to_datetime(date)
    except TypeError:
        date = date
    try:
        year = int(date.year)
    except (AttributeError, ValueError):
        year = np.nan
    try:
        month = int(date.month)
    except (AttributeError, ValueError):
        month = np.nan
    try:
        day = int(date.day)
    except (AttributeError, ValueError):
        day = np.nan
    try:
        hour = date.hour + date.minute / 60.0 + date.second / 3600.0
    except (AttributeError, ValueError):
        hour = np.nan
    return {"year": year, "month": month, "day": day, "hour": hour}


def pentad_to_month_day(p: int) -> tuple[int, int]:
    """
    Given a pentad number, return the month and day of the first day in the pentad.

    Parameters
    ----------
    p: int
        Pentad number from 1 to 73

    Returns
    -------
    tuple of int
        A tuple of two ints representing month and day of the first day of the pentad.
    """
    if not (0 < p < 74):
        raise ValueError(f"Invalid p: {p}. Must be between 1 and 73")
    m = [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        2,
        2,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
        3,
        3,
        4,
        4,
        4,
        4,
        4,
        4,
        5,
        5,
        5,
        5,
        5,
        5,
        5,
        6,
        6,
        6,
        6,
        6,
        6,
        7,
        7,
        7,
        7,
        7,
        7,
        8,
        8,
        8,
        8,
        8,
        8,
        9,
        9,
        9,
        9,
        9,
        9,
        10,
        10,
        10,
        10,
        10,
        10,
        11,
        11,
        11,
        11,
        11,
        11,
        12,
        12,
        12,
        12,
        12,
        12,
    ]
    d = [
        1,
        6,
        11,
        16,
        21,
        26,
        31,
        5,
        10,
        15,
        20,
        25,
        2,
        7,
        12,
        17,
        22,
        27,
        1,
        6,
        11,
        16,
        21,
        26,
        1,
        6,
        11,
        16,
        21,
        26,
        31,
        5,
        10,
        15,
        20,
        25,
        30,
        5,
        10,
        15,
        20,
        25,
        30,
        4,
        9,
        14,
        19,
        24,
        29,
        3,
        8,
        13,
        18,
        23,
        28,
        3,
        8,
        13,
        18,
        23,
        28,
        2,
        7,
        12,
        17,
        22,
        27,
        2,
        7,
        12,
        17,
        22,
        27,
    ]
    return m[p - 1], d[p - 1]


def valid_month_day(year: int | None = None, month: int = 1, day: int = 1) -> bool:
    """
    Returns True if month and day combination are allowed, False otherwise. Assumes that Feb 29th is valid.

    Parameters
    ----------
    year: int, optional, default: None
        Year to be tested
        If none, set year to default leap year
    month: int, default: 1
        Month to be tested
    day: int, default: 1
        Day to be tested

    Returns
    -------
    bool
        True if month and day (or year month and day) are a valid combination (e.g. 12th March) and False if not
        (e.g. 30th February)

    Notes
    -----
    Assumes that February 29th is a valid date.
    """
    if year is None:
        year = 2004

    if month < 1 or month > 12:
        return False
    month_lengths = get_month_lengths(year)
    if day < 1 or day > month_lengths[month - 1]:
        return False

    return True


def which_pentad_array(month: np.ndarray, day: np.ndarray):
    """
    Take month and day arrays as inputs and return array of pentads in range 1-73.

    Parameters
    ----------
    month: ndarray
        Month containing the day for which we want to calculate the pentad.
    day: ndarray
        Day for the day for which we want to calculate the pentad.

    Returns
    -------
    ndarray
        Pentad (5-day period) containing input day, from 1 (1 Jan-5 Jan) to 73 (27-31 Dec).
    """
    pentad = ((day_in_year_array(month=month, day=day) - 1) / 5).astype(int)
    return pentad + 1


def day_in_year_array(month: np.ndarray, day: np.ndarray) -> np.ndarray:
    """
    Get the day in year from 1 to 365. Leap years are dealt with by allowing Feb 29 and Mar 1 to be the same day.

    Parameters
    ----------
    month: 1D np.ndarray
        Array of months
    day: 1D np.ndarray
        Array of days

    Returns
    -------
    np.ndarray
        Array of day number from 1-365.
    """
    cumulative_month_lengths = np.array([0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334])
    day_number = cumulative_month_lengths[month - 1] + day
    return day_number


def which_pentad(month: int, day: int) -> int:
    """
    Take month and day as inputs and return pentad in range 1-73.

    Parameters
    ----------
    month: int
        Month containing the day for which we want to calculate the pentad.
    day: int
        Day for the day for which we want to calculate the pentad.

    Returns
    -------
    int
        Pentad (5-day period) containing input day, from 1 (1 Jan-5 Jan) to 73 (27-31 Dec).

    Raises
    ------
    ValueError
        If month not in range 1-12 or day not in range 1-31

    Note
    ----
    The calculation is rather simple. It just loops through the year and adds up days till it reaches
    the day we are interested in. February 29th is treated as though it were March 1st in a regular year.
    """
    if not valid_month_day(month=month, day=day):
        raise ValueError(f"Invalid month {month} - day {day} combination.")

    pentad = int((day_in_year(month=month, day=day) - 1) / 5)
    pentad = pentad + 1

    assert 1 <= pentad <= 73  # noqa: S101

    return pentad


def day_in_year(year: int | None = None, month: int = 1, day: int = 1) -> int:
    """
    Get the day in year from 1 to 365 or 366.

    Parameters
    ----------
    year: int, optional, default: None
        Year to be tested
        If none, set year to default leap year
    month: int, default: 1
        Month to be tested
    day: int, default: 1
        Day to be tested

    Returns
    -------
    int
        Day in year. If year is not specified then the year is treated as a non-leap year and
        29 February returns the same value as 1 March.
    """
    year_not_specified = False
    if year is None:
        year = 2004
        year_not_specified = True

    if not valid_month_day(year=year, month=month, day=day):
        raise ValueError(f"Invalid year {year} - month {month} - day {day} combination.")

    if year_not_specified:
        year = 2003

    month_lengths = get_month_lengths(year)

    if month == 1:
        day_index = day
    elif year_not_specified and month == 2 and day == 29:
        day_index = day_in_year(month=3, day=1)
    else:
        day_index = np.sum(month_lengths[0 : month - 1]) + day

    assert (not year_not_specified and (1 <= day_index <= 366)) or (  # noqa: S101
        year_not_specified and (1 <= day_index <= 365)
    )

    return day_index


def relative_year_number(year: int, reference: int = 1979) -> int:
    """
    Get number of year relative to reference year (1979 by default).

    Parameters
    ----------
    year : int
        Year
    reference : int, default: 1979
        Reference year

    Returns
    -------
    int
        Number of year relative to reference year.
    """
    return year - (reference + 1)


def convert_time_in_hours(hour: int, minute: int, sec: int, zone: int | float, daylight_savings_time: float) -> float:
    """
    Convert integer hour, minute, and second to time in decimal hours

    Parameters
    ----------
    hour : int
        Hour
    minute : int
        Minute
    sec : int
        Second
    zone : int or float
        Correction for timezone
    daylight_savings_time : float
        Set to 1 if daylight savings time is in effect else set to 0

    Returns
    -------
    float
        Time converted to decimal hour in day
    """
    return hour + (minute + sec / 60.0) / 60.0 + zone - daylight_savings_time


def leap_year(years_since_1980: int) -> int:
    """
    Is input year a Leap year?

    Parameters
    ----------
    years_since_1980: int
        Number of years since 1980

    Returns
    -------
    int
        1 if it is a leap year, 0 otherwise
    """
    return math.floor(years_since_1980 / 4.0)


def time_in_whole_days(time_in_hours: int, day: int, years_since_1980: int, leap: int) -> float:
    """
    Calculate from time in hours to time in whole days.

    Parameters
    ----------
    time_in_hours: int
        Time in hours
    day: int
        Day number
    years_since_1980: int
        Number of years since 1980
    leap: int
        Set to 1 for a leap year, else set to 0

    Returns
    -------
    float
        Time in whole days.
    """
    return years_since_1980 * 365 + leap + day - 1.0 + time_in_hours / 24.0


def leap_year_correction(time_in_hours: float, day: int, years_since_1980: int) -> float:
    """
    Make leap year correction.

    Parameters
    ----------
    time_in_hours: float
        Time in hours
    day: int
        Day number
    years_since_1980: int
        Years since 1980

    Returns
    -------
    float
        Leap year corrected time.
    """
    leap = leap_year(years_since_1980)
    time = time_in_whole_days(time_in_hours, day, years_since_1980, leap)
    if years_since_1980 == leap * 4.0:
        time = time - 1.0
    if years_since_1980 < 0 and years_since_1980 != leap * 4.0:
        time = time - 1.0
    return time


def jul_day(year: int, month: int, day: int) -> int:
    """
    Routine to calculate julian day. This is the weird Astronomical thing which counts from 1 Jan 4713 BC.

    Parameters
    ----------
    year: int
        Year.
    month: int
        Month.
    day: int
        Day.

    Returns
    -------
    int
        Julian day.

    Note
    ----
    This is one of those routines that looks baffling but works. No one is sure exactly how. It gets
    written once and then remains untouched for centuries, mysteriously working.
    """
    if not valid_month_day(month=month, day=day):
        raise ValueError(f"Invalid month {month} - day {day} combination.")

    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def get_month_lengths(year: int) -> list[int]:
    """
    Return a list holding the lengths of the months in a given year

    Parameters
    ----------
    year : int
        Year for which you want month lengths

    Returns
    -------
    list of int
        List of month lengths
    """
    if calendar.isleap(year):
        month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    return month_lengths


def convert_date_to_hours(dates: Sequence[datetime]) -> Sequence[float]:
    """
    Convert an array of datetimes to an array of hours since the first element.

    Parameters
    ----------
    dates: array-like of datetime, shape (n,)
        1-dimensional date array.

    Returns
    -------
    array-like of float, shape (n,)
        1- dimensional array containing hours since the first element in the array.
    """
    n_dates = len(dates)
    hours_elapsed = np.zeros(n_dates)
    for i, date in enumerate(dates):
        duration_in_seconds = (date - dates[0]).total_seconds()
        hours_elapsed[i] = duration_in_seconds / (60 * 60)
    return hours_elapsed


@post_format_return_type(["times1", "times2"], dtype=float)
@inspect_arrays(["times1", "times2"])
def time_difference(times1, times2):
    """
    Calculate time difference in hours between any two times.

    Parameters
    ----------
    year1: int
        Year of first time point.
    month1: int
        Month of first time point.
    day1: int
        Day of first time point.
    hour1: int
        Hour of first time point.
    year2: int
        Year of second time point.
    month2: int
        Month of second time point.
    day2: int
        Day of second time point.
    hour2: int
        Hour of second time point.

    Returns
    -------
    float
        Difference in hours between the two times.
    """
    # docstring !!!
    times1 = pd.to_datetime(times1, errors="coerce").values
    times2 = pd.to_datetime(times2, errors="coerce").values

    valid = isvalid(times1) & isvalid(times2)

    result = np.full(times1.shape, np.nan, dtype=float)  # np.ndarray
    result[valid] = (times2[valid] - times1[valid]).astype(float) / (1e9 * 60 * 60)
    return result
