from enum import Enum


class TimeIntervalUnitType(str, Enum):
    """Enum representing units of time for intervals.

    This enum defines standard time units used to specify intervals or durations in
    time-based operations, such as scheduling, timeouts, or pagination. Each value
    represents a unit of time, from seconds to years, and inherits from `str` to allow
    seamless integration with string-based APIs or databases.
    """

    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEAR = "year"
