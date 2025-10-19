# -*- coding: utf-8 -*-
"""FAT date time implementation."""

import decimal

from dfdatetime import definitions
from dfdatetime import factory
from dfdatetime import interface


class FATDateTimeEpoch(interface.DateTimeEpoch):
  """FAT date time time epoch."""

  def __init__(self):
    """Initializes a FAT date time epoch."""
    super(FATDateTimeEpoch, self).__init__(1980, 1, 1)


class FATDateTime(interface.DateTimeValues):
  """FAT date time.

  The FAT date time is mainly used in DOS/Windows file formats and FAT.

  The FAT date and time is a 32-bit value containing two 16-bit values:
    * The date (lower 16-bit).
      * bits 0 - 4: day of month, where 1 represents the first day
      * bits 5 - 8: month of year, where 1 represent January
      * bits 9 - 15: year since 1980
    * The time of day (upper 16-bit).
      * bits 0 - 4: seconds (in 2 second intervals)
      * bits 5 - 10: minutes
      * bits 11 - 15: hours

  The FAT date time has no time zone information and is typically stored
  in the local time of the computer.

  Attributes:
    is_local_time (bool): True if the date and time value is in local time.
  """

  _EPOCH = FATDateTimeEpoch()

  # The difference between January 1, 1980 and January 1, 1970 in seconds.
  _FAT_DATE_TO_POSIX_BASE = 315532800

  def __init__(self, fat_date_time=None, precision=None, time_zone_offset=None):
    """Initializes a FAT date time.

    Args:
      fat_date_time (Optional[int]): FAT date time.
      precision (Optional[str]): precision of the date and time value, which
          should be one of the PRECISION_VALUES in definitions.
      time_zone_offset (Optional[int]): time zone offset in number of minutes
          from UTC or None if not set.
    """
    super(FATDateTime, self).__init__(
        precision=precision or definitions.PRECISION_2_SECONDS,
        time_zone_offset=time_zone_offset)
    self._fat_date_time = fat_date_time
    self._number_of_seconds = None

    if fat_date_time is not None:
      self._number_of_seconds = self._GetNumberOfSeconds(fat_date_time)

  @property
  def fat_date_time(self):
    """int: FAT date time or None if not set."""
    return self._fat_date_time

  def _GetNormalizedTimestamp(self):
    """Retrieves the normalized timestamp.

    Returns:
      decimal.Decimal: normalized timestamp, which contains the number of
          seconds since January 1, 1970 00:00:00 and a fraction of second used
          for increased precision, or None if the normalized timestamp cannot be
          determined.
    """
    if self._normalized_timestamp is None:
      if self._number_of_seconds is not None and self._number_of_seconds >= 0:
        self._normalized_timestamp = (
            decimal.Decimal(self._number_of_seconds) +
            self._FAT_DATE_TO_POSIX_BASE)

        if self._time_zone_offset:
          self._normalized_timestamp -= self._time_zone_offset * 60

    return self._normalized_timestamp

  def _GetNumberOfSeconds(self, fat_date_time):
    """Retrieves the number of seconds from a FAT date time.

    Args:
      fat_date_time (int): FAT date time.

    Returns:
      int: number of seconds since January 1, 1980 00:00:00.

    Raises:
      ValueError: if the month, day of month, hours, minutes or seconds
          value is out of bounds.
    """
    day_of_month = fat_date_time & 0x1f
    month = (fat_date_time >> 5) & 0x0f
    year = (fat_date_time >> 9) & 0x7f

    days_per_month = self._GetDaysPerMonth(year, month)
    if day_of_month < 1 or day_of_month > days_per_month:
      raise ValueError('Day of month value out of bounds.')

    number_of_days = self._GetDayOfYear(1980 + year, month, day_of_month)
    number_of_days -= 1
    for past_year in range(0, year):
      number_of_days += self._GetNumberOfDaysInYear(past_year)

    fat_date_time >>= 16

    seconds = (fat_date_time & 0x1f) * 2
    minutes = (fat_date_time >> 5) & 0x3f
    hours = (fat_date_time >> 11) & 0x1f

    if hours not in range(0, 24):
      raise ValueError('Hours value out of bounds.')

    if minutes not in range(0, 60):
      raise ValueError('Minutes value out of bounds.')

    if seconds not in range(0, 60):
      raise ValueError('Seconds value out of bounds.')

    number_of_seconds = (((hours * 60) + minutes) * 60) + seconds
    number_of_seconds += number_of_days * definitions.SECONDS_PER_DAY
    return number_of_seconds

  def CopyFromDateTimeString(self, time_string):
    """Copies a FAT date time from a date and time string.

    Args:
      time_string (str): date and time value formatted as:
          YYYY-MM-DD hh:mm:ss.######[+-]##:##

          Where # are numeric digits ranging from 0 to 9 and the seconds
          fraction can be either 3, 6 or 9 digits. The time of day, seconds
          fraction and time zone offset are optional. The default time zone
          is UTC.

    Raises:
      ValueError: if the time string is invalid or not supported.
    """
    date_time_values = self._CopyDateTimeFromString(time_string)

    year = date_time_values.get('year', 0)
    month = date_time_values.get('month', 0)
    day_of_month = date_time_values.get('day_of_month', 0)
    hours = date_time_values.get('hours', 0)
    minutes = date_time_values.get('minutes', 0)
    seconds = date_time_values.get('seconds', 0)
    time_zone_offset = date_time_values.get('time_zone_offset', None)

    if year < 1980 or year > (1980 + 0x7f):
      raise ValueError(f'Year value not supported: {year!s}.')

    self._normalized_timestamp = None
    self._number_of_seconds = self._GetNumberOfSecondsFromElements(
        year, month, day_of_month, hours, minutes, seconds)
    self._number_of_seconds -= self._FAT_DATE_TO_POSIX_BASE
    self._time_zone_offset = time_zone_offset

  def CopyToDateTimeString(self):
    """Copies the FAT date time to a date and time string.

    Returns:
      str: date and time value formatted as: "YYYY-MM-DD hh:mm:ss" or None
          if number of seconds is missing.
    """
    if self._number_of_seconds is None:
      return None

    number_of_days, hours, minutes, seconds = self._GetTimeValues(
        self._number_of_seconds)

    year, month, day_of_month = self._GetDateValuesWithEpoch(
        number_of_days, self._EPOCH)

    return (f'{year:04d}-{month:02d}-{day_of_month:02d} '
            f'{hours:02d}:{minutes:02d}:{seconds:02d}')


class FATTimestamp(interface.DateTimeValues):
  """FAT timestamp.

  The FAT timestamp is an unsigned integer that contains the number of
  10 milli seconds intervals since 1980-01-01 00:00:00 (also known as
  the FAT date time epoch).

  Attributes:
    is_local_time (bool): True if the date and time value is in local time.
  """

  _EPOCH = FATDateTimeEpoch()

  # The difference between January 1, 1980 and January 1, 1970 in seconds.
  _FAT_DATE_TO_POSIX_BASE = 315532800

  def __init__(self, precision=None, time_zone_offset=None, timestamp=None):
    """Initializes a FAT timestamp.

    Args:
      precision (Optional[str]): precision of the date and time value, which
          should be one of the PRECISION_VALUES in definitions.
      time_zone_offset (Optional[int]): time zone offset in number of minutes
          from UTC or None if not set.
      timestamp (Optional[int]): FAT timestamp.
    """
    super(FATTimestamp, self).__init__(
        precision=precision or definitions.PRECISION_10_MILLISECONDS,
        time_zone_offset=time_zone_offset)
    self._timestamp = timestamp

  @property
  def timestamp(self):
    """int: FAT timestamp or None if not set."""
    return self._timestamp

  def _GetNormalizedTimestamp(self):
    """Retrieves the normalized timestamp.

    Returns:
      decimal.Decimal: normalized timestamp, which contains the number of
          seconds since January 1, 1970 00:00:00 and a fraction of second used
          for increased precision, or None if the normalized timestamp cannot be
          determined.
    """
    if self._normalized_timestamp is None:
      if self._timestamp is not None:
        self._normalized_timestamp = (
            (decimal.Decimal(self._timestamp) / 100) +
            self._FAT_DATE_TO_POSIX_BASE)

        if self._time_zone_offset:
          self._normalized_timestamp -= self._time_zone_offset * 60

    return self._normalized_timestamp

  def CopyFromDateTimeString(self, time_string):
    """Copies a FAT timestamp from a date and time string.

    Args:
      time_string (str): date and time value formatted as:
          YYYY-MM-DD hh:mm:ss.######[+-]##:##

          Where # are numeric digits ranging from 0 to 9 and the seconds
          fraction can be either 3, 6 or 9 digits. The time of day, seconds
          fraction and time zone offset are optional. The default time zone
          is UTC.

    Raises:
      ValueError: if the time string is invalid or not supported.
    """
    date_time_values = self._CopyDateTimeFromString(time_string)

    year = date_time_values.get('year', 0)
    month = date_time_values.get('month', 0)
    day_of_month = date_time_values.get('day_of_month', 0)
    hours = date_time_values.get('hours', 0)
    minutes = date_time_values.get('minutes', 0)
    seconds = date_time_values.get('seconds', 0)
    nanoseconds = date_time_values.get('nanoseconds', 0)
    time_zone_offset = date_time_values.get('time_zone_offset', None)

    if year < 1980 or year > (1980 + 0x7f):
      raise ValueError(f'Year value not supported: {year!s}.')

    milliseconds, _ = divmod(nanoseconds, 10000000)

    timestamp = self._GetNumberOfSecondsFromElements(
        year, month, day_of_month, hours, minutes, seconds)
    timestamp -= self._FAT_DATE_TO_POSIX_BASE
    timestamp *= 100
    timestamp += milliseconds

    self._timestamp = timestamp
    self._time_zone_offset = time_zone_offset

  def CopyToDateTimeString(self):
    """Copies the FAT timestamp to a date and time string.

    Returns:
      str: date and time value formatted as: "YYYY-MM-DD hh:mm:ss.######" or
          None if the timestamp is missing.
    """
    if self._timestamp is None:
      return None

    timestamp, milliseconds = divmod(self._timestamp, 100)
    number_of_days, hours, minutes, seconds = self._GetTimeValues(timestamp)

    year, month, day_of_month = self._GetDateValuesWithEpoch(
        number_of_days, self._EPOCH)

    return (f'{year:04d}-{month:02d}-{day_of_month:02d} '
            f'{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:02d}')


factory.Factory.RegisterDateTimeValues(FATDateTime)
factory.Factory.RegisterDateTimeValues(FATTimestamp)
