"""Common pandas utilities"""

__all__ = ["convert_to_numeric", "reindex_state_year"]

import numpy as np
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
        series = series.map(lambda x: round(x) if not np.isnan(x) else x)
    except:
        raise

    return series


def reindex_state_year(df: pd.DataFrame) -> pd.DataFrame:
    """Update the index of the data frame

    Args:
        df (pd.DataFrame): Data frame to update index of.

    Returns:
        pd.DataFrame: Data frame with updated index.
    """
    # Add year to index
    index_list = df.index.to_list()

    # Rearrange indices
    new_index = []
    position = {}
    for i, index in enumerate(index_list):
        if index[0] == "ALABAMA":
            position[index[1]] = i
        elif index[0] == "U.S. TOTAL":
            new_index.insert(position[index[1]], index)
            continue

        new_index.append(index)

    # Reindex
    new_index = pd.MultiIndex.from_tuples(new_index, names=["STATE", "year"])
    assert len(new_index) == df.shape[0]
    df = df.reindex(new_index)

    return df
    return df
