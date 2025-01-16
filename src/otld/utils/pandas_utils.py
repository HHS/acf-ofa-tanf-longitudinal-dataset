"""Common pandas utilities"""

__all__ = ["convert_to_numeric", "get_header", "excel_to_dict"]

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
