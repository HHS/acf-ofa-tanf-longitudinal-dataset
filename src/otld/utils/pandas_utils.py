"""Common pandas utilities"""

__all__ = ["convert_to_numeric"]

import pandas as pd

from otld.utils.string_utils import make_negative_string


def convert_to_numeric(series: pd.Series, numeric_type: type = float) -> pd.Series:
    """Convert the elements in a series to integers

    Args:
        series (pd.Series): Pandas series to conver to integer type.

    Returns:
        pd.Series: Series converted to type int.
    """
    try:
        series = series.map(
            lambda x: (make_negative_string(x) if type(x) is str else x)
        )
        series = series.astype(numeric_type)
    except:
        raise

    return series
