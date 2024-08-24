# %%
import re
from datetime import timedelta

import polars as pl


def pl_print(df):
    with pl.Config(tbl_hide_column_data_types=True):
        print(df)


def parse_timedelta_string(time_str):
    """
    Parse a human-readable duration string into a `timedelta` object.

    The function accepts strings representing durations with units of
    days, hours, minutes, and seconds (e.g., "2d10s", "60m", "1h30m").
    The string can be in any order, and the function will correctly sum
    the units to create the appropriate `timedelta` object.

    Parameters
    ----------
    time_str : str
        A string representing the duration. The string can contain
        multiple time units in any order, such as '2d5h10m', '3h15s',
        '60m', etc. Supported units are:
            - 'd' for days
            - 'h' for hours
            - 'm' for minutes
            - 's' for seconds

    Returns
    -------
    timedelta
        A `timedelta` object representing the parsed duration.

    Raises
    ------
    ValueError
        If the input string cannot be parsed into a valid duration.

    Examples
    --------
    >>> parse_timedelta_string("60m")
    datetime.timedelta(seconds=3600)

    >>> parse_timedelta_string("2d5h10m")
    datetime.timedelta(days=2, seconds=18600)
    """
    # Define the regex pattern to match time units (e.g., 2d, 3h, 60m, 10s)
    pattern = r"(?P<value>\d+)(?P<unit>[dhms])"

    # Create a dictionary to map units to keyword arguments for timedelta
    unit_mapping = {
        "d": "days",
        "h": "hours",
        "m": "minutes",
        "s": "seconds",
    }

    # Initialize a dictionary to hold the time units
    time_params = {"days": 0, "hours": 0, "minutes": 0, "seconds": 0}

    # List to maintain the order of encountered units
    units_order = ["d", "h", "m", "s"]
    last_seen_index = -1

    # Find all matches in the input string
    matches = re.finditer(pattern, time_str)

    for match in matches:
        value = int(match.group("value"))
        unit = match.group("unit")

        # Check if the current unit is in the correct order
        current_index = units_order.index(unit)
        if current_index < last_seen_index:
            raise ValueError(
                f"Invalid order: '{unit}' appears after a smaller unit in '{time_str}'"
            )
        last_seen_index = current_index

        # Add the value to the corresponding time unit in the dictionary
        time_param = unit_mapping[unit]
        time_params[time_param] += value

    # Create and return the timedelta object
    return timedelta(**time_params)


def timedelta_to_string(td):
    """
    Convert a `timedelta` object to a string in H:M:S format.

    Parameters
    ----------
    td : timedelta
        The `timedelta` object to be converted.

    Returns
    -------
    str
        A string representing the duration in H:M:S format.

    Examples
    --------
    >>> td = timedelta(hours=5, minutes=30, seconds=15)
    >>> timedelta_to_hms_string(td)
    '5:30:15'

    >>> td = timedelta(days=1, hours=2, minutes=3, seconds=4)
    >>> timedelta_to_hms_string(td)
    '26:03:04'
    """
    if td is None:
        return None

    total_seconds = int(td.total_seconds())

    days, remainder = divmod(total_seconds, int(timedelta(days=1).total_seconds()))
    hours, remainder = divmod(total_seconds, int(timedelta(hours=1).total_seconds()))
    minutes, seconds = divmod(remainder, int(timedelta(minutes=1).total_seconds()))

    days_str = f"{days}d " if days else ""
    return f"{days_str}{hours}:{minutes:02}:{seconds:02}"


# %%
