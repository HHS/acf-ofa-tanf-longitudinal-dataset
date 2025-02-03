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


# How does get_header work if there are merged cells?
def get_header(
    df: pd.DataFrame,
    column: str | int = None,
    find: str = None,
    reset: bool = False,
    sanitize: bool = False,
    idx: bool = False,
    concatenate: bool = False,
) -> int | pd.DataFrame | pd.Series:
    """Find and extract the header row from a data frame

    If only a data frame is provided, finds the first row in which all columns have a
    non-missing value and uses this as the header. Otherwise, searches in column `column`
    for the first occurrence of value `find` and uses that row as the header.

    Args:
        df (pd.DataFrame): A data frame to search within.
        column (str | int, optional): A column to search within for value `find`.
            Defaults to None.
        find (str, optional): A value to search for within `column`. Defaults to None.
        reset (bool, optional): Boolean indicating whether the index should be reset before searching
            for the header. Defaults to False.
        sanitize (bool, optional): A boolean indicating whether to manipulate column
            headers before searching them. Defaults to False.
        idx (bool, optional): A boolean indicating whether to return simply the
            row index of the header rather than the series containin the header.
            Defaults to False.

    Returns:
        int | pd.DataFrame | pd.Series: Returns a data frame with leading rows removed
            and the header updated if only a data frame is provided. Otherwise returns
            either an integer index or a series containing potential column names.
    """
    df = df.copy()
    if reset:
        df.reset_index(inplace=True)

    def known_header(
        df: pd.DataFrame, column: str | int, find: str, sanitize: bool, idx: bool
    ) -> int | pd.Series:
        """Handle the case where the header is known"""

        assert column is not None, "Must specify a column to search within."
        assert find is not None, "Must specify a string to find."

        if sanitize:
            index = df[
                df.loc[:, column].apply(lambda x: bool(re.search(find, str(x).lower())))
            ]
        else:
            index = df[df.loc[:, column].apply(lambda x: bool(re.search(find, str(x))))]

        # Get first match
        index = index.index.min()

        if idx:
            return index

        return df.loc[index]

    def unknown_header(df: pd.DataFrame, concatenate: bool = False) -> pd.DataFrame:
        """Handle the case where the header is unknown"""

        # Drop any columns which only contain missing values
        df.dropna(axis=1, how="all", inplace=True)
        header = 0
        columns = df.loc[header, :]

        # Identify first row with no missing values
        while True:
            if bool(columns.isna().any()) is False:
                break

            header += 1
            if concatenate:
                columns.fillna("", inplace=True)
                new_columns = df.loc[header, :].fillna("")
                columns = [
                    f"{col} {new}".strip() if f"{col} {new}".strip() else np.nan
                    for col, new in zip(columns, new_columns)
                ]
                columns = pd.Series(columns)
            else:
                columns = df.loc[header, :]

        # Set column names to the header row
        df.columns = columns

        # Keep only rows after the header row
        df = df.loc[header + 1 :, :]

        return df

    if column or find:
        return known_header(df, column, find, sanitize, idx)
    else:
        return unknown_header(df, concatenate)


def excel_to_dict(path: str, custom_args: dict = None, **kwargs) -> dict[pd.DataFrame]:
    """Convert an Excel workbook to a dictionary of data frames

    Args:
        path (str): Path to an Excel workbook
        custom_args (dict, optional):Any arguments to be passed to read_excel. Defaults to None.

    Returns:
        dict[pd.DataFrame]: Dictionary of data frames.
    """
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

    file.close()

    return dictionary


def dict_to_excel(dictionary: dict, path: str, **kwargs) -> None:
    """Convert a dictionary of dictionaries to an Excel workbook

    Args:
        dictionary (dict): A dictionary containing dictionaries. The key will become the
        name of the tab.
        path (str): The path to the Excel file.
    """
    writer = pd.ExcelWriter(path)
    for tab in dictionary:
        pd.DataFrame.from_dict(dictionary[tab], **kwargs).to_excel(
            writer, sheet_name=tab, index=False
        )

    writer.close()
