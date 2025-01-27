"""This module combines appended files across the 2014-2015 disjunction."""

import os
import re

import pandas as pd

from otld.paths import input_dir, inter_dir
from otld.utils import missingness, validate_data_frame
from otld.utils.crosswalk_2014_2015 import crosswalk, crosswalk_dict, map_columns
from otld.utils.expenditure_utils import reindex_state_year


def get_column_list(crosswalk: pd.DataFrame, column: str | int) -> list[str]:
    """Extract names as list from a column of crosswalk data frame

    Args:
        crosswalk (pd.DataFrame): Pandas data frame crosswalking ACF-196 and ACF-196R
        column (str | int): The column to extract names from

    Returns:
        list: A list of string column names
    """
    columns = crosswalk[column].dropna().to_list()
    columns = [str(c) for c in columns]
    columns = ",".join(columns)
    columns = columns.split(",")
    columns = [c.strip() for c in columns]

    return columns


def reorder_alpha_numeric(values: list | pd.Series) -> list:
    """Sort alphanumeric values

    Args:
        values (list | pd.Series): A list of alphanumeric values.

    Returns:
        list: A sorted list of alphanumeric values

    Examples:
        >>> reorder_alpha_numeric(["1", "11", "2", "2b", "1a", "2a"])
        ["1", "1a", "2", "2a", "2b", "11"]
    """
    values = [re.search(r"(\d+)(\w*)", value).groups() for value in values]
    values = [(int(value[0]), value[1]) for value in values]
    values.sort()
    values = [(str(value[0]), value[1]) for value in values]
    values = ["".join(value) for value in values]

    return values


def format_state_index(value: tuple) -> tuple:
    """Adjust the formatting of the state index.

    Args:
        value (tuple): Index tuple.

    Returns:
        tuple: Index tuple with state adjusted.
    """
    state_name = value[0].title()
    state_name = (
        "District of Columbia" if state_name.startswith("Dist.") else state_name
    )

    return state_name, value[1]


def consolidate_categories(row: pd.Series, df: pd.DataFrame) -> None:
    """Consolidate Funding categories (for visualization)

    Args:
        row (pd.Series): Row containing consolidation instructions and new variable name.
        df (pd.DataFrame): DataFrame in which to create new columns.
    """

    columns = str(row["instructions"]).split(",")
    try:
        in_columns = [column in df.columns for column in columns]
        assert all(in_columns)
    except AssertionError:
        present = []
        for i, val in enumerate(in_columns):
            if val is True:
                present.append(columns[i])

        columns = present

    df[row["name"]] = df[columns].sum(axis=1)


def main() -> dict[pd.DataFrame]:
    """Entry point for combine_appended_files.py"""

    columns_196 = get_column_list(crosswalk, 196)
    columns_196_r = get_column_list(crosswalk, "196R")

    files = os.listdir(inter_dir)
    federal = []
    state = []

    # Append files to relevant lists
    for file in files:
        if not file.startswith("federal") and not file.startswith("state"):
            continue
        df = pd.read_csv(os.path.join(inter_dir, file), index_col=["STATE", "year"])
        level = "state" if file.startswith("state") else "federal"

        if file.find("2015_2023") > -1:
            df = df.filter(columns_196_r)
        else:
            df = df.filter(columns_196)
            df = map_columns(df, crosswalk_dict)

        if level == "federal":
            federal.append(df)
        elif level == "state":
            state.append(df)

    # Append data frames and reorder columns
    rename_dict = {
        key: f"{key}. " + value["name"] for key, value in crosswalk_dict.items()
    }

    state = pd.concat(state)
    state = state[reorder_alpha_numeric(state.columns)]
    state.drop(["1", "2", "3", "4", "5", "7", "8"], inplace=True, axis=1)

    federal = pd.concat(federal)
    federal = federal[reorder_alpha_numeric(federal.columns)]

    frames = {"Federal": federal, "State": state}

    missingness.main(frames)

    total = federal.add(state, fill_value=0)
    total.sort_index(level=["year", "STATE"], inplace=True)
    total = reindex_state_year(total)
    total = total[reorder_alpha_numeric(total.columns)]

    for df in [total, federal, state]:
        # Calculate consolidated_categories
        consolidated_categories = pd.read_excel(
            os.path.join(input_dir, "Instruction Crosswalk.xlsx"),
            sheet_name="consolidated_categories",
        )
        consolidated_categories.apply(
            lambda row: consolidate_categories(row, df), axis=1
        )
        # Title case the state names
        df.index = pd.MultiIndex.from_tuples(
            df.index.map(format_state_index), names=["State", "FiscalYear"]
        )
        df.rename(columns=rename_dict, inplace=True)
        df.drop(index="Puerto Rico", level=0, inplace=True)

        validate_data_frame(df)

    frames.update({"Total": total})

    return frames


if __name__ == "__main__":
    main()
