"""Common pandas utilities"""

__all__ = ["convert_to_numeric", "reindex_state_year", "get_header", "excel_to_dict"]

import re

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


def reindex_state_year(
    df: pd.DataFrame, names: list[str] = ["STATE", "year"]
) -> pd.DataFrame:
    """Update the index of the data frame

    Args:
        df (pd.DataFrame): Data frame to update index of.

    Returns:
        pd.DataFrame: Data frame with updated index.
    """
    # Convert index to list
    index_list = df.index.to_list()

    new_index = []
    position = {}

    # Find where year and state are in index
    for i, name in enumerate(df.index.names):
        if name.lower().find("year") > -1:
            year_pos = i

        if name.lower().find("state") > -1:
            state_pos = i

    # Where in the list to move the U.S. Total index
    for i, index in enumerate(index_list):
        if index[state_pos].lower() == "alabama":
            position[index[year_pos]] = i
        elif index[state_pos].lower() == "u.s. total":
            new_index.insert(position[index[year_pos]], index)
            continue

        new_index.append(index)

    # Reindex
    new_index = pd.MultiIndex.from_tuples(new_index, names=names)
    assert len(new_index) == df.shape[0]
    df = df.reindex(new_index)

    return df


def get_header(
    df: pd.DataFrame,
    column: str | int = None,
    find: str = None,
    reset: bool = False,
    sanitize: bool = False,
    idx: bool = False,
) -> int | pd.DataFrame:
    df = df.copy()
    if reset:
        df.reset_index(inplace=True)

    def known_header(
        df: pd.DataFrame, column: str | int, find: str, sanitize: bool, idx: bool
    ):
        assert column is not None, "Must specify a column to search within."
        assert find is not None, "Must specify a string to find."
        if sanitize:
            index = df[
                df.loc[:, column].apply(lambda x: bool(re.search(find, str(x).lower())))
            ]
        else:
            index = df[df.loc[:, column].apply(lambda x: bool(re.search(find, str(x))))]

        index = index.index.min()

        if idx:
            return index

        return df.loc[index]

    def unknown_header(df: pd.DataFrame) -> pd.DataFrame:
        df.dropna(axis=1, how="all", inplace=True)
        header = 0
        while True:
            if bool(df.loc[header, :].isna().any()) is False:
                break

            header += 1

        df.columns = df.loc[header, :]
        df = df.loc[header + 1 :, :]

        return df

    if column or find:
        return known_header(df, column, find, sanitize, idx)
    else:
        return unknown_header(df)


def excel_to_dict(path: str, custom_args: dict = None, **kwargs):
    file = pd.ExcelFile(path)
    sheets = file.sheet_names
    if custom_args:
        try:
            dictionary = {
                sheet: pd.read_excel(file, sheet_name=sheet, **custom_args[sheet])
                for sheet in sheets
            }
        except:
            raise

    else:
        dictionary = {
            sheet: pd.read_excel(file, sheet_name=sheet, **kwargs) for sheet in sheets
        }

    return dictionary
