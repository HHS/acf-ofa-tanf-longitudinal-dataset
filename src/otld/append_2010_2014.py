"""Append Excel workbooks for 2010-2014"""

import json
import os
import re

import openpyxl
import pandas as pd

from otld.paths import input_dir, inter_dir
from otld.utils import delete_empty_columns, get_column_names, standardize_line_number


def rename_columns(df: pd.DataFrame, sheet: str, column_dict: dict) -> pd.DataFrame:
    """Rename TANF dataframe columns

    Rename TANF dataframe columns to line numbers.

    Args:
        df (pd.DataFrame): Dataframe in which to rename columns.
        sheet (str): Sheet the data came from.
        column_dict (dict): Dictionary to use to convert column name to line number.

    Raises:
        ValueError: _description_

    Returns:
        pd.DataFrame: _description_
    """
    # Select the line number for the relevant sheet
    if sheet.endswith("Non-Assistance"):
        number = 6
    elif sheet.endswith("Assistance"):
        number = 5
    elif sheet.endswith("Non-A Subcategories"):
        number = 6
    else:
        raise ValueError("Invalid sheet")

    # Select columns associated with the line number
    if sheet.endswith("Subcategories"):
        column_dict = {
            key: value
            for key, value in column_dict.items()
            if key.startswith("6a") or key.startswith("6c")
        }
    else:
        column_dict = {
            key: value
            for key, value in column_dict.items()
            if key.startswith(str(number)) and key.find("(") == -1
        }

    # Rename columns
    columns = ["STATE"]
    columns.extend(column_dict.keys())
    df.columns = [standardize_line_number(column) for column in columns]

    return df


def get_tanf_df(
    tanf_path: str | os.PathLike, sheets: list[str], year: int
) -> pd.DataFrame:
    """Get data from TANF Financial files

    Args:
        tanf_path (str | os.PathLike): Path to TANF file.
        sheets (list[str]): List of sheets to extract.
        year (int): The year associated with the Excel workbook.

    Returns:
        pd.DataFrame: Appended workbooks as data frames.
    """
    data = []
    tanf_excel_file = openpyxl.load_workbook(tanf_path)

    for sheet in sheets:
        # Use openpyxl to get column names and delete columns with no data
        tanf_df = tanf_excel_file[sheet]
        delete_empty_columns(tanf_df)
        columns, i = get_column_names(tanf_df)

        # Read in data with pandas and rename columns
        tanf_df = pd.read_excel(tanf_path, sheet_name=sheet, skiprows=i, header=None)
        tanf_df.columns = columns
        tanf_df = rename_columns(tanf_df, sheet, column_dict)

        # Clean up and add to data list
        tanf_df.dropna(subset=["STATE"], inplace=True)
        tanf_df.set_index("STATE", inplace=True)
        data.append(tanf_df)

    # Concatenate and remove duplicated columns
    tanf_df = pd.concat(data, axis=1)
    tanf_df = tanf_df.loc[:, ~tanf_df.columns.duplicated()]
    tanf_df["year"] = year

    return tanf_df


def main():
    """Entry point for appending 2010-2014"""

    # Select tanf files
    tanf_path = os.path.join(input_dir, "2010_2023")
    tanf_files = os.scandir(tanf_path)
    federal = []
    state = []

    # Select sheets
    sheets = ["Assistance", "Non-Assistance", "Non-A Subcategories"]
    fed_sheets = [f"Federal {sheet}" for sheet in sheets]
    state_sheets = [f"State {sheet}" for sheet in sheets]

    for file in tanf_files:
        # Extract year from file name
        file_year = re.search(r"(\d{4}).xlsx?", str(file.path)).group(1)
        file_year = int(file_year)
        if file_year >= 2015:
            continue

        federal_df = get_tanf_df(file.path, fed_sheets, file_year)
        state_df = get_tanf_df(file.path, state_sheets, file_year)

        federal.append(federal_df)
        state.append(state_df)

    # Concatenate all years and reset index
    federal_df = pd.concat(federal).reset_index()
    state_df = pd.concat(state).reset_index()

    # Export
    federal_df.to_csv(os.path.join(inter_dir, "federal_2010_2014.csv"), index=False)
    state_df.to_csv(os.path.join(inter_dir, "state_2010_2014.csv"), index=False)


if __name__ == "__main__":
    # Load column dictionary for 196 instructions
    with open(os.path.join(input_dir, "column_dict_196.json"), "r") as file:
        column_dict = json.load(file)
    main()
