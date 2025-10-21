"""
QC of individual reports
========================

Module containing main QC functions which could be applied on a DataBundle.
"""

from __future__ import annotations

import numpy as np

from .astronomical_geometry import sunangle
from .auxiliary import (
    ValueDatetimeType,
    ValueFloatType,
    ValueIntType,
    convert_units,
    failed,
    format_return_type,
    inspect_arrays,
    isvalid,
    passed,
    post_format_return_type,
    untestable,
)
from .external_clim import ClimFloatType, inspect_climatology
from .time_control import convert_date, day_in_year, get_month_lengths


vectorized_day_in_year = np.vectorize(day_in_year)
vectorized_sunangle = np.vectorize(sunangle, otypes=[float, float, float, float, float, float])


@post_format_return_type(["value"])
@inspect_arrays(["value"])
def value_check(value: ValueFloatType) -> ValueIntType:
    """
    Check if a value is equal to None or numerically invalid (NaN).

    Parameters
    ----------
    value : float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float
        The input value(s) to be tested.
        Can be a scalar, sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.

    Returns
    -------
    Same type as input, but with integer values
        - Returns 1 (or array/sequence/Series of 1s) if the input value is None or numerically invalid (NaN)
        - Returns 0 (or array/sequence/Series of 0s) otherwise.
    """
    valid_mask = isvalid(value)
    result = np.where(valid_mask, passed, failed)

    return result


@post_format_return_type(["lat", "lon"])
@inspect_arrays(["lat", "lon"])
@convert_units(lat="degrees", lon="degrees")
def do_position_check(lat: ValueFloatType, lon: ValueFloatType) -> ValueIntType:
    """
    Perform the positional QC check on the report. Simple check to make sure that the latitude and longitude are
    within specified bounds: latitude is between -90 and 90. Longitude is between
    -180 and 360

    Parameters
    ----------
    lat : float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float
        Latitude(s) of observation in degrees.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    lon : float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float
        Longitude() of observation in degrees.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.

    Returns
    -------
    Same type as input, but with integer values
        - Returns 2 (or array/sequence/Series of 2s) if either latitude or longitude is numerically invalid (None/NaN).
        - Returns 1 (or array/sequence/Series of 1s) if either latitude or longitude is out of the valid range.
        - Returns 0 (or array/sequence/Series of 0s) otherwise.
    """
    result = np.full(lat.shape, untestable, dtype=int)  # type: np.ndarray

    valid_indices = isvalid(lat) & isvalid(lon)

    cond_failed = np.full(lat.shape, True, dtype=bool)  # type: np.ndarray
    cond_failed[valid_indices] = (lat[valid_indices] < -90) | (lat[valid_indices] > 90) | (lon[valid_indices] < -180) | (lon[valid_indices] > 360)

    result[valid_indices & cond_failed] = failed
    result[valid_indices & ~cond_failed] = passed

    return result


@post_format_return_type(["date", "year"])
@convert_date(["year", "month", "day"])
@inspect_arrays(["year", "month", "day"])
def do_date_check(
    date: ValueDatetimeType = None,
    year: ValueIntType = None,
    month: ValueIntType = None,
    day: ValueIntType = None,
) -> ValueIntType:
    """
    Perform the date QC check on the report. Checks whether the given date or date components are valid.

    Parameters
    ----------
    date: datetime, None, sequence of datetime or None, 1D np.ndarray of datetime, or pd.Series of float, optional
        Date(s) of observation.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    year : int, None, sequence of int or None, 1D np.ndarray of int, or pd.Series of int, optional
        Year(s) of observation.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    month : int, None, sequence of int or None, 1D np.ndarray of int, or pd.Series of int, optional
        Month(s) of observation (1-12).
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    day : int, None, sequence of int or None, 1D np.ndarray of int, or pd.series of int, optional
        Day(s) of observation.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.

    Returns
    -------
    Same type as input, but with integer values
        - Returns 2 (or array/sequence/Series of 2s) if any of year, month, or day is numerically invalid or None,
        - Returns 1 (or array/sequence/Series of 1s) if the date is not valid,
        - Returns 0 (or array/sequence/Series of 0s) otherwise.
    """
    result = np.full(year.shape, untestable, dtype=int)
    valid = isvalid(year) & isvalid(month) & isvalid(day)

    year_valid = year[valid].astype(int)
    month_valid = month[valid].astype(int)
    day_valid = day[valid].astype(int)

    result_valid = np.full(year_valid.shape, failed, dtype=int)

    year_ok = (year_valid >= 1850) & (year_valid <= 2025)
    month_ok = (month_valid >= 1) & (month_valid <= 12)

    unique_years = np.unique(year_valid)
    month_length_map = {y: get_month_lengths(y) for y in unique_years}
    max_days = np.array([month_length_map[y][m - 1] for y, m in zip(year_valid, month_valid, strict=False)])

    day_ok = (day_valid >= 1) & (day_valid <= max_days)

    passed_mask = year_ok & month_ok & day_ok

    result_valid[passed_mask] = passed

    result[valid] = result_valid

    return result


@post_format_return_type(["date", "hour"])
@convert_date(["hour"])
@inspect_arrays(["hour"])
def do_time_check(date: ValueDatetimeType = None, hour: ValueFloatType = None) -> ValueIntType:
    """
    Check that the time is valid i.e. in the range 0.0 to 23.99999...

    Parameters
    ----------
    date: datetime, None, sequence of datetime or None, 1D np.ndarray of datetime, or pd.Series of float, optional
        Date(s) of observation.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    hour: float, None, sequence of float or None, 1D np.ndarray of float, or pd.Series of float, optional
        Hour(s) of observation (minutes as decimal).
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.

    Returns
    -------
    Same type as input, but with integer values
        - Returns 2 (or array/sequence/Series of 2s) if hour is numerically invalid or None,
        - Returns 1 (or array/sequence/Series of 1s) if hour is not a valid hour,
        - Returns 0 (or array/sequence/Series of 0s) otherwise.
    """
    result = np.full(hour.shape, untestable, dtype=int)  # type: np.ndarray

    valid_indices = isvalid(hour)

    cond_failed = np.full(hour.shape, True, dtype=bool)  # type: np.ndarray
    cond_failed[valid_indices] = (hour[valid_indices] >= 24) | (hour[valid_indices] < 0)

    result[valid_indices & cond_failed] = failed
    result[valid_indices & ~cond_failed] = passed

    return result


def _do_daytime_check(date, year, month, day, hour, lat, lon, time_since_sun_above_horizon, mode):
    if mode not in ["day", "night"]:
        raise ValueError(f"mode: {mode} is not in valid list ['day', 'night']")

    p_check = np.atleast_1d(do_position_check(lat, lon))
    d_check = np.atleast_1d(do_date_check(year=year, month=month, day=day))
    t_check = np.atleast_1d(do_time_check(hour=hour))

    result = np.full(year.shape, untestable, dtype=int)

    if mode == "day":
        _failed = failed
        _passed = passed
    else:
        _failed = passed
        _passed = failed

    failed_mask = (p_check == failed) | (d_check == failed) | (t_check == failed)
    result[failed_mask] = failed

    valid_mask = (~failed_mask) & (p_check != untestable) & (d_check != untestable) & (t_check != untestable)
    if not np.any(valid_mask):
        return result

    valid_indices = np.where(valid_mask)[0]

    year_valid = year[valid_indices].astype(int)
    month_valid = month[valid_indices].astype(int)
    day_valid = day[valid_indices].astype(int)
    hour_valid = hour[valid_indices]

    doy = vectorized_day_in_year(year_valid, month_valid, day_valid)
    hour_whole = np.floor(hour_valid)
    minute_valid = (hour_valid - hour_whole) * 60.0

    if time_since_sun_above_horizon is not None:
        hour_whole -= time_since_sun_above_horizon

    lat_fixed = lat[valid_indices]
    lat_fixed[lat_fixed == 0] = 0.0001
    lon_fixed = lon[valid_indices]
    lon_fixed[lon_fixed == 0] = 0.0001

    underflow = hour_whole < 0
    hour_whole[underflow] += 24
    doy[underflow] -= 1

    fix_indices = underflow & (doy <= 0)
    if np.any(fix_indices):
        year_valid[fix_indices] -= 1
        doy[fix_indices] = vectorized_day_in_year(year_valid[fix_indices], 12, 31)

    _azimuths, elevations, _rtas, _hras, _sids, _decs = vectorized_sunangle(
        year_valid,
        doy.astype(int),
        hour_whole.astype(int),
        minute_valid,
        0,
        0,
        0,
        lat_fixed,
        lon_fixed,
    )

    # Assign results in one go
    result[valid_indices] = np.where(elevations > 0, _passed, _failed)

    return result


@post_format_return_type(["date", "year"])
@convert_date(["year", "month", "day", "hour"])
@inspect_arrays(["year", "month", "day", "hour", "lat", "lon"])
@convert_units(lat="degrees", lon="degrees")
def do_day_check(
    date: ValueDatetimeType = None,
    year: ValueIntType = None,
    month: ValueIntType = None,
    day: ValueIntType = None,
    hour: ValueFloatType = None,
    lat: ValueFloatType = None,
    lon: ValueFloatType = None,
    time_since_sun_above_horizon: float | None = None,
) -> ValueIntType:
    """
    Determine if the sun was above the horizon a specified time before the report (`time_since_sub_above_horizon`)
    based on date, time, and position.

    This "day" test is used to classify Marine Air Temperature (MAT) measurements as either
    Night MAT (NMAT) or Day MAT, accounting for solar heating biases and a potential lag between sun rise and the
    onset of significant warming. It calculates the sun's elevation using the `sunangle` function, offset by the
    specified `time_since_sun_above_horizon`.

    Parameters
    ----------
    date: datetime, None, sequence of datetime or None, 1D np.ndarray of datetime, or pd.Series of float, optional
        Date(s) of observation.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    year : int, None, sequence of int or None, 1D np.ndarray of int, or pd.Series of int, optional
        Year(s) of observation.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    month : int, None, sequence of int or None, 1D np.ndarray of int, or pd.Series of int, optional
        Month(s) of observation (1-12).
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    day : int, None, sequence of int or None, 1D np.ndarray of int, or pd.series of int, optional
        Day(s) of observation.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    hour : float, None, sequence of float or None, 1D np.ndarray of float, or pd.Series of float, optional
        Hour(s) of observation (minutes as decimal).
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    lat : float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float
        Latitude(s) of observation in degrees.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    lon : float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float
        Longitude() of observation in degree.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    time_since_sun_above_horizon : float
        Maximum time sun can have been above horizon (or below) to still count as night. Original QC test had this set
        to 1.0 i.e. it was night between one hour after sundown and one hour after sunrise.

    Returns
    -------
    Same type as input, but with integer values
        - Returns 2 (or array/sequence/Series of 2s) if any of do_position_check, do_date_check, or do_time_check
          returns 2.
        - Returns 1 (or array/sequence/Series of 1s) if any of do_position_check, do_date_check, or do_time_check
          returns 1 or if it is night (sun below horizon an hour ago).
        - Returns 0 if it is day (sun above horizon an hour ago).

    Note
    ----
    In previous versions, ``time_since_sun_above_horizon`` has the default value 1.0 as one hour is used as a
    definition of "day" for marine air temperature QC. Solar heating biases were considered to be negligible mmore
    than one hour after sunset and up to one hour after sunrise.

    See Also
    --------
    do_night_check: Determine if the sun was above the horizon an hour ago based on date, time, and position.
    """
    return _do_daytime_check(date, year, month, day, hour, lat, lon, time_since_sun_above_horizon, mode="day")


@post_format_return_type(["date", "year"])
@convert_date(["year", "month", "day", "hour"])
@inspect_arrays(["year", "month", "day", "hour", "lat", "lon"])
@convert_units(lat="degrees", lon="degrees")
def do_night_check(
    date: ValueDatetimeType = None,
    year: ValueIntType = None,
    month: ValueIntType = None,
    day: ValueIntType = None,
    hour: ValueFloatType = None,
    lat: ValueFloatType = None,
    lon: ValueFloatType = None,
    time_since_sun_above_horizon: float | None = None,
) -> ValueIntType:
    """
    Determine if the sun was below the horizon a specified time before the report (`time_since_sub_above_horizon`)
    based on date, time, and position.

    This "night" test is used to classify Marine Air Temperature (MAT) measurements as either
    Night MAT (NMAT) or Day MAT, accounting for solar heating biases and a potential lag between sun rise and the
    onset of significant warming. It calculates the sun's elevation using the `sunangle` function, offset by the
    specified `time_since_sun_above_horizon`.

    Parameters
    ----------
    date: datetime, None, sequence of datetime or None, 1D np.ndarray of datetime, or pd.Series of float, optional
        Date(s) of observation.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    year : int, None, sequence of int or None, 1D np.ndarray of int, or pd.Series of int, optional
        Year(s) of observation.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    month : int, None, sequence of int or None, 1D np.ndarray of int, or pd.Series of int, optional
        Month(s) of observation (1-12).
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    day : int, None, sequence of int or None, 1D np.ndarray of int, or pd.series of int, optional
        Day(s) of observation.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    hour : float, None, sequence of float or None, 1D np.ndarray of float, or pd.Series of float, optional
        Hour(s) of observation (minutes as decimal).
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    lat : float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float
        Latitude(s) of observation in degrees.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    lon : float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float
        Longitude() of observation in degree.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    time_since_sun_above_horizon : float
        Maximum time sun can have been above horizon (or below) to still count as night. Original QC test had this set
        to 1.0 i.e. it was night between one hour after sundown and one hour after sunrise.

    Returns
    -------
    Same type as input, but with integer values
        - Returns 2 (or array/sequence/Series of 2s) if any of do_position_check, do_date_check, or do_time_check
          returns 2.
        - Returns 1 (or array/sequence/Series of 1s) if any of do_position_check, do_date_check, or do_time_check
          returns 1 or if it is day (sun above horizon an hour ago).
        - Returns 0 if it is night (sun below horizon an hour ago).

    Note
    ----
    In previous versions, ``time_since_sun_above_horizon`` has the default value 1.0 as one hour is used as a
    definition of "day" for marine air temperature QC. Solar heating biases were considered to be negligible mmore
    than one hour after sunset and up to one hour after sunrise.

    See Also
    --------
    do_day_check: Determine if the sun was above the horizon an hour ago based on date, time, and position.
    """
    return _do_daytime_check(
        date,
        year,
        month,
        day,
        hour,
        lat,
        lon,
        time_since_sun_above_horizon,
        mode="night",
    )


def do_missing_value_check(value: ValueFloatType) -> ValueIntType:
    """
    Check if a value is equal to None or numerically invalid (NaN).

    Parameters
    ----------
    value : float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float
        The input value(s) to be tested.
        Can be a scalar, sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.

    Returns
    -------
    Same type as input, but with integer values
        - Returns 1 (or array/sequence/Series of 1s) if the input value is None or numerically invalid (NaN)
        - Returns 0 (or array/sequence/Series of 0s) otherwise.
    """
    return value_check(value)


@inspect_climatology("climatology")
def do_missing_value_clim_check(climatology: ClimFloatType, **kwargs) -> ValueIntType:
    """
    Check if a climatological value is equal to None or numerically invalid (NaN).

    Parameters
    ----------
    climatology : float, None, sequence of float or None, 1D np.ndarray of float, pd.Series of float or :py:class:`.Climatology`
        The input climatological value(s) to be tested.
        Can be a scalar, sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.

    Returns
    -------
    Same type as input, but with integer values
        - Returns 1 (or array/sequence/Series of 1s) if the input value is None or numerically invalid (NaN)
        - Returns 0 (or array/sequence/Series of 0s) otherwise.

    Note
    ----
    If `climatology` is a :py:class:`.Climatology` object, pass `lon` and `lat` and `date`, or `month` and `day`, as keyword
    arguments to extract the relevant climatological value.
    """
    return value_check(climatology)


@post_format_return_type(["value"])
@inspect_arrays(["value"])
@convert_units(value="unknown", limits="unknown")
def do_hard_limit_check(
    value: ValueFloatType,
    limits: tuple[float, float],
) -> ValueIntType:
    """
    Check if a value is outside specified limits.

    Parameters
    ----------
    value: float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float
        The value(s) to be tested against the limits.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    limits: tuple of float
        A tuple of two floats representing the lower and upper limit.

    Returns
    -------
    Same type as input, but with integer values
        - Returns 2 (or array/sequence/Series of 2s) if the upper limit is less than or equal
          to the lower limit, or if the input is invalid (None or NaN).
        - Returns 1 (or array/sequence/Series of 1s) if value(s) are outside the specified limits.
        - Returns 0 (or array/sequence/Series of 0s) if value(s) are within limits.
    """
    result = np.full(value.shape, untestable, dtype=int)  # type: np.ndarray

    if limits[1] <= limits[0]:
        return format_return_type(result, value)

    valid_indices = isvalid(value)

    cond_passed = np.full(value.shape, True, dtype=bool)  # type: np.ndarray
    cond_passed[valid_indices] = (limits[0] <= value[valid_indices]) & (value[valid_indices] <= limits[1])

    result[valid_indices & cond_passed] = passed
    result[valid_indices & ~cond_passed] = failed

    return result


@post_format_return_type(["value"])
@inspect_arrays(["value", "climatology"])
@convert_units(value="unknown", climatology="unknown")
@inspect_climatology("climatology", optional="standard_deviation")
def do_climatology_check(
    value: ValueFloatType,
    climatology: ClimFloatType,
    maximum_anomaly: float,
    standard_deviation: ValueFloatType = "default",
    standard_deviation_limits: tuple[float, float] | None = None,
    lowbar: float | None = None,
) -> ValueIntType:
    """
    Climatology check to compare a value with a climatological average within specified anomaly limits.
    This check supports optional parameters to customize the comparison.

    If ``standard_deviation`` is provided, the value is converted into a standardised anomaly. Optionally,
    if ``standard deviation`` is outside the range specified by ``standard_deviation_limits`` then
    ``standard_deviation`` is set to whichever of the lower or upper limits is closest.
    If ``lowbar`` is provided, the anomaly must be greater than ``lowbar`` to fail regardless of ``standard_deviation``.

    Parameters
    ----------
    value: float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float
        Value(s) to be compared to climatology.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    climatology : float, None, sequence of float or None, 1D np.ndarray of float, pd.Series of float or :py:class:`.Climatology`
        The climatological average(s) to which the values(s) will be compared.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    maximum_anomaly: float
        Largest allowed anomaly.
        If ``standard_deviation`` is provided, this is interpreted as the largest allowed standardised anomaly.
    standard_deviation: float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float,
        default: "default"
        The standard deviation(s) used to standardise the anomaly
        If set to "default", it is internally treated as 1.0.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    standard_deviation_limits: tuple of float, optional
        A tuple of two floats representing the upper and lower limits for standard deviation used in the check.
    lowbar: float, optional
        The anomaly must be greater than lowbar to fail regardless of standard deviation.

    Returns
    -------
    Same type as input, but with integer values
        - Returns 2 (or array/sequence/Series of 2s) if `standard_deviation_limits[1]` is less than or equal to
          `standard_deviation_limits[0]`, or if `maximum_anomaly` is less than or equal to 0, or if any of
          `value`, `climate_normal`, or `standard_deviation` is numerically invalid (None or NaN).
        - Returns 1 (or array/sequence/Series of 1s) if the difference is outside the specified range.
        - Returns 0 (or array/sequence/Series of 0s) otherwise.

    Note
    ----
    If either `climatology` or `standard_deviation` is a :py:class:`.Climatology` object, pass `lon` and `lat` and
    `date`, or `month` and `day`, as keyword arguments to extract the relevant climatological value(s).
    """
    if climatology.ndim == 0:
        climatology = np.full_like(value, climatology)  # type: np.ndarray

    if isinstance(standard_deviation, str) and standard_deviation == "default":
        standard_deviation = np.full(value.shape, 1.0, dtype=float)
    standard_deviation = np.atleast_1d(standard_deviation)  # type: np.ndarray

    result = np.full(value.shape, untestable, dtype=int)  # type: np.ndarray

    if maximum_anomaly is None or maximum_anomaly <= 0:
        return format_return_type(result, value)

    if standard_deviation_limits is None:
        standard_deviation_limits = (0, np.inf)
    elif standard_deviation_limits[1] <= standard_deviation_limits[0]:
        return format_return_type(result, value)

    valid_indices = isvalid(value) & isvalid(climatology) & isvalid(maximum_anomaly) & isvalid(standard_deviation)
    standard_deviation[valid_indices] = np.clip(
        standard_deviation[valid_indices],
        standard_deviation_limits[0],
        standard_deviation_limits[1],
    )

    climate_diff = np.zeros_like(value)  # type: np.ndarray

    climate_diff[valid_indices] = np.abs(value[valid_indices] - climatology[valid_indices])

    if lowbar is None:
        low_check = np.ones(value.shape, dtype=bool)  # type: np.ndarray
    else:
        low_check = climate_diff > lowbar

    cond_failed = np.full(value.shape, False, dtype=bool)  # type: np.ndarray
    cond_failed[valid_indices] = (climate_diff[valid_indices] / standard_deviation[valid_indices] > maximum_anomaly) & low_check[valid_indices]

    result[valid_indices & cond_failed] = failed
    result[valid_indices & ~cond_failed] = passed

    return result


@post_format_return_type(["dpt", "at2"])
@inspect_arrays(["dpt", "at2"])
@convert_units(dpt="K", at2="K")
def do_supersaturation_check(dpt: ValueFloatType, at2: ValueFloatType) -> ValueIntType:
    """
    Perform the super saturation check. Check if a valid dewpoint temperature is greater than a valid air temperature

    Parameters
    ----------
    dpt : float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float
        Dewpoint temperature value(s).
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    at2 : float, None, sequence of float or None, 1D np.ndarray of float or pd.Series of float
        Air temperature values(s).
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.

    Returns
    -------
    Same type as input, but with integer values
        - Returns 2 (or array/sequence/Series of 2s) if either dpt or at2 is invalid (None or NaN).
        - Returns 1 (or array/sequence/Series of 1s) if supersaturation is detected,
        - Returns 0 (or array/sequence/Series of 0s) otherwise.
    """
    result = np.full(dpt.shape, untestable, dtype=int)  # type: np.ndarray

    valid_indices = isvalid(dpt) & isvalid(at2)

    cond_failed = np.full(dpt.shape, True, dtype=bool)  # type: np.ndarray
    cond_failed[valid_indices] = dpt[valid_indices] > at2[valid_indices]

    result[valid_indices & cond_failed] = failed
    result[valid_indices & ~cond_failed] = passed

    return result


@post_format_return_type(["sst"])
@inspect_arrays(["sst"])
@convert_units(sst="K", freezing_point="K")
def do_sst_freeze_check(
    sst: ValueFloatType,
    freezing_point: float,
    freeze_check_n_sigma: float | None = "default",
    sst_uncertainty: float | None = "default",
) -> ValueIntType:
    """
    Check input sea-surface temperature(s) to see if it is above freezing.

    This is a simple freezing point check made slightly more complex. We want to check if a
    measurement of SST is above freezing, but there are two problems. First, the freezing point
    can vary from place to place depending on the salinity of the water. Second, there is uncertainty
    in SST measurements. If we place a hard cut-off at -1.8C, then we are likely to bias the average
    of many measurements too high when they are near the freezing point - observational error will
    push the measurements randomly higher and lower, and this test will trim out the lower tail, thus
    biasing the result. The inclusion of an SST uncertainty parameter *might* mitigate that, and we allow
    that possibility here. Note also that many ships make sea-surface temperature measurements to the nearest
    whole degree, which in the case of water at or close to freezing would round to -2C and would fail a naive
    test.

    Parameters
    ----------
    sst : float, None, sequence of float or None, 1D np.ndarray of float or pd.series of float
        Input sea-surface temperature value(s) to be checked.
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    freezing_point : float, optional
        The freezing point of the water.
    freeze_check_n_sigma : float, optional, default: "default"
        Number of uncertainty standard deviations that sea surface temperature can be
        below the freezing point before the QC check fails.
    sst_uncertainty : float, optional, default: "default"
        the uncertainty in the SST value

    Returns
    -------
    Same type as input, but with integer values
        - Returns 2 (or array/sequence/Series of 2s) if any of `sst`, `freezing_point`, `sst_uncertainty`,
          or `n_sigma` is numerically invalid (None or NaN).
        - Returns 1 (or array/sequence/Series of 1s) if `sst` is below `freezing_point` by more than
          `n_sigma` times `sst_uncertainty`.
        - Returns 0 (or array/sequence/Series of 0s) otherwise.

    Note
    ----
    In previous versions, some parameters had default values:

        * ``sst_uncertainty``: 0.0
        * ``freezing_point``: -1.80
        * ``n_sigma``: 2.0
    """
    result = np.full(sst.shape, untestable, dtype=int)  # type: np.ndarray

    if not isvalid(sst_uncertainty) or not isvalid(freezing_point) or not isvalid(freeze_check_n_sigma):
        return result

    valid_sst = isvalid(sst)

    if freeze_check_n_sigma == "default":
        freeze_check_n_sigma = 0.0

    if sst_uncertainty == "default":
        sst_uncertainty = 0.0

    cond_failed = np.full(sst.shape, True, dtype=bool)  # type: np.ndarray
    cond_failed[valid_sst] = sst[valid_sst] < (freezing_point - freeze_check_n_sigma * sst_uncertainty)

    result[valid_sst & cond_failed] = failed
    result[valid_sst & ~cond_failed] = passed

    return result


@post_format_return_type(["wind_speed", "wind_direction"])
@inspect_arrays(["wind_speed", "wind_direction"])
def do_wind_consistency_check(wind_speed: ValueFloatType, wind_direction: ValueFloatType) -> ValueIntType:
    """
    Test to compare windspeed to winddirection to check if they are consistent. Zero windspeed should correspond
    to no particular direction (variable) and wind speeds above a threshold should correspond to a particular
    direction.

    Parameters
    ----------
    wind_speed : float, None, sequence of float or None, 1D np.ndarray of float or pd.series of float
        Wind speed value(s).
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.
    wind_direction : float, None, sequence of float or None, 1D np.ndarray of float or pd.series of float
        Wind direction value(s).
        Can be a scalar, a sequence (e.g., list or tuple), a one-dimensional NumPy array, or a pandas Series.

    Returns
    -------
    Same type as input, but with integer values
        - Returns 2 (or array/sequence/Series of 2s) if either wind_speed or wind_direction is invalid (None or NaN).
        - Returns 1 (or array/sequence/Series of 1s) if wind_speed and wind_direction are inconsistent,
        - Returns 0 (or array/sequence/Series of 0s) otherwise.
    """
    result = np.full(wind_speed.shape, untestable, dtype=int)  # type: np.ndarray

    valid_indices = isvalid(wind_speed) & isvalid(wind_direction)

    cond_failed = np.full(wind_speed.shape, True, dtype=bool)  # type: np.ndarray
    cond_failed[valid_indices] = ((wind_speed[valid_indices] == 0) & (wind_direction[valid_indices] != 0)) | (
        (wind_speed[valid_indices] != 0) & (wind_direction[valid_indices] == 0)
    )

    result[valid_indices & cond_failed] = failed
    result[valid_indices & ~cond_failed] = passed

    return result
