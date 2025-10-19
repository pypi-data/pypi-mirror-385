# -*- coding: utf-8 -*-
"""Delphi TDateTime implementation."""

import decimal

from dfdatetime import definitions
from dfdatetime import factory
from dfdatetime import interface


class DelphiDateTimeEpoch(interface.DateTimeEpoch):
  """Delphi TDateTime epoch."""

  def __init__(self):
    """Initializes a Delphi TDateTime epoch."""
    super(DelphiDateTimeEpoch, self).__init__(1899, 12, 30)


class DelphiDateTime(interface.DateTimeValues):
  """Delphi TDateTime timestamp.

  The Delphi TDateTime timestamp is a floating point value that contains
  the number of days since 1899-12-30 00:00:00 (also known as the epoch).
  Negative values represent date and times predating the epoch.

  The maximal correct date supported by TDateTime values is limited to:
  9999-12-31 23:59:59.999

  Attributes:
    is_local_time (bool): True if the date and time value is in local time.
  """

  # The difference between December 30, 1899 and January 1, 1970 in days.
  _DELPHI_TO_POSIX_BASE = 25569

  _EPOCH = DelphiDateTimeEpoch()

  def __init__(self, precision=None, time_zone_offset=None, timestamp=None):
    """Initializes a Delphi TDateTime timestamp.

    Args:
      precision (Optional[str]): precision of the date and time value, which
          should be one of the PRECISION_VALUES in definitions.
      time_zone_offset (Optional[int]): time zone offset in number of minutes
          from UTC or None if not set.
      timestamp (Optional[float]): Delphi TDateTime timestamp.
    """
    super(DelphiDateTime, self).__init__(
        precision=precision or definitions.PRECISION_1_MILLISECOND,
        time_zone_offset=time_zone_offset)
    self._timestamp = timestamp

  @property
  def timestamp(self):
    """float: Delphi TDateTime timestamp or None if not set."""
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
            decimal.Decimal(self._timestamp) - self._DELPHI_TO_POSIX_BASE)
        self._normalized_timestamp *= definitions.SECONDS_PER_DAY

        if self._time_zone_offset:
          self._normalized_timestamp -= self._time_zone_offset * 60

    return self._normalized_timestamp

  def CopyFromDateTimeString(self, time_string):
    """Copies a Delphi TDateTime timestamp from a string.

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

    if year > 9999:
      raise ValueError(f'Unsupported year value: {year:d}.')

    timestamp = self._GetNumberOfSecondsFromElements(
        year, month, day_of_month, hours, minutes, seconds)

    timestamp = float(timestamp) / definitions.SECONDS_PER_DAY
    timestamp += self._DELPHI_TO_POSIX_BASE
    timestamp += float(nanoseconds) / definitions.NANOSECONDS_PER_DAY

    self._normalized_timestamp = None
    self._timestamp = timestamp
    self._time_zone_offset = time_zone_offset

  def CopyToDateTimeString(self):
    """Copies the Delphi TDateTime timestamp to a date and time string.

    Returns:
      str: date and time value formatted as: "YYYY-MM-DD hh:mm:ss.######" or
          None if the timestamp is missing.
    """
    if self._timestamp is None:
      return None

    number_of_seconds = self._timestamp * definitions.SECONDS_PER_DAY

    number_of_days, hours, minutes, seconds = self._GetTimeValues(
        int(number_of_seconds))

    # The maximum date supported by TDateTime values is limited to:
    # 9999-12-31 23:59:59.999 (approximate 2958465 days since epoch).
    # The minimum date is unknown hence assuming it is limited to:
    # 0001-01-01 00:00:00.000 (approximate -693593 days since epoch).
    if number_of_days < -693593 or number_of_days > 2958465:
      return None

    year, month, day_of_month = self._GetDateValuesWithEpoch(
        number_of_days, self._EPOCH)

    microseconds = int(
        (number_of_seconds % 1) * definitions.MICROSECONDS_PER_SECOND)

    return (f'{year:04d}-{month:02d}-{day_of_month:02d} '
            f'{hours:02d}:{minutes:02d}:{seconds:02d}.{microseconds:06d}')


factory.Factory.RegisterDateTimeValues(DelphiDateTime)
