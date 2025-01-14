"""Append Excel workbooks for 2010-2014"""

import json
import os
import re

import openpyxl
import pandas as pd

from otld.paths import diagnostics_dir, input_dir, inter_dir
from otld.utils import (
    ExpenditureDataChecker,
    convert_to_numeric,
    delete_empty_columns,
    get_column_names,
    standardize_line_number,
    validate_data_frame,
)
from otld.utils.LineTracker import LineTracker

line_tracker = LineTracker()


def rename_columns(
    df: pd.DataFrame, sheet: str, column_dict: dict, tracker: dict
) -> pd.DataFrame:
    """Rename TANF dataframe columns

    Rename TANF dataframe columns to line numbers.

    Args:
        df (pd.DataFrame): Dataframe in which to rename columns.
        sheet (str): Sheet the data came from.
        column_dict (dict): Dictionary to use to convert column name to line number.
        tracker (dict): Dictionary tracking column names before and after renaming.

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
    elif sheet.startswith("Summary"):
        df = df.iloc[:, [0, 1, 2, 4, 5, 7, 8, 9]].copy()
        tracker["BaseColumns"] = df.columns.to_list()
        df.columns = ["STATE", "1", "Carryover", "2", "3", "7", "9", "10"]
        tracker["RenamedColumns"] = df.columns.to_list()
        df["4"] = df["1"] - df["2"] - df["3"]
        return df
    elif sheet.startswith("Total"):
        df = df.iloc[:, [0, 1]].copy()
        tracker["BaseColumns"] = df.columns.to_list()
        df.columns = ["STATE", "7"]
        tracker["RenamedColumns"] = df.columns.to_list()
        return df
    else:
        raise ValueError("Invalid sheet")

    tracker["BaseColumns"] = df.columns.to_list()

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

    tracker["RenamedColumns"] = df.columns.to_list()

    return df


def get_tanf_df(
    tanf_path: str | os.PathLike,
    sheets: list[str],
    year: int,
    column_dict: dict,
    level: str,
) -> pd.DataFrame:
    """Get data from TANF Financial files

    Args:
        tanf_path (str | os.PathLike): Path to TANF file.
        sheets (list[str]): List of sheets to extract.
        year (int): The year associated with the Excel workbook.
        column_dict (dict): A dictionary mapping line numbers to field names.
        level (str): Level of data: "State" or "Federal".

    Returns:
        pd.DataFrame: Appended workbooks as data frames.
    """
    data = []
    tanf_excel_file = openpyxl.load_workbook(tanf_path)

    path_stem = os.path.split(tanf_path)[1]

    for sheet in sheets:
        # Begin building tracker dictionary
        tracker = {"FileName": path_stem, "SheetName": sheet, "Level": level}

        # Use openpyxl to get column names and delete columns with no data
        tanf_df = tanf_excel_file[sheet]
        delete_empty_columns(tanf_df)
        columns, i = get_column_names(tanf_df)

        # Read in data with pandas and rename columns
        tanf_df = pd.read_excel(tanf_path, sheet_name=sheet, skiprows=i, header=None)
        tanf_df.columns = columns

        tanf_df = rename_columns(tanf_df, sheet, column_dict, tracker)
        assert len(tracker["BaseColumns"]) == len(tracker["RenamedColumns"])

        # Filter rows
        tanf_df.dropna(subset=["STATE"], inplace=True)
        tanf_df = tanf_df[~tanf_df["STATE"].str.startswith("Footnote")]
        tanf_df["STATE"] = tanf_df["STATE"].map(lambda x: x.strip())
        tanf_df.set_index("STATE", inplace=True)

        # Append to data list
        line_tracker.sources[year].append(tracker)
        data.append(tanf_df)

    # Concatenate and remove duplicated columns
    tanf_df = pd.concat(data, axis=1)
    tanf_df = tanf_df.loc[:, ~tanf_df.columns.duplicated()]

    # Convert columns to int
    tanf_df = tanf_df.apply(convert_to_numeric)
    tanf_df.fillna(0, inplace=True)

    # Add year
    tanf_df["year"] = year

    return tanf_df


def main(export: bool = False) -> tuple[pd.DataFrame]:
    """Entry point for appending 2010-2014

    Args:
        export (bool): Export csv versions of the data frames.

    Returns:
        tuple[pd.DataFrame]: Federal and state appended data frames for 1997-2009
    """

    # Load column dictionary for 196 instructions
    with open(os.path.join(input_dir, "column_dict_196.json"), "r") as file:
        column_dict = json.load(file)

    # Select tanf files
    tanf_path = os.path.join(input_dir, "2010_2023")
    tanf_files = os.scandir(tanf_path)
    federal = []
    state = []

    # Select sheets
    sheets = [
        "Assistance",
        "Non-Assistance",
        "Non-A Subcategories",
    ]
    fed_sheets = [f"Federal {sheet}" for sheet in sheets]
    fed_sheets += ["Summary Federal Funds"]
    state_sheets = [f"State {sheet}" for sheet in sheets]
    state_sheets += ["Total State Expenditure Summary"]

    for file in tanf_files:
        # Extract year from file name
        year = re.search(r"(\d{4}).xlsx?", str(file.path)).group(1)
        year = int(year)
        if year >= 2015:
            continue

        line_tracker.sources[year] = []
        federal_df = get_tanf_df(file.path, fed_sheets, year, column_dict, "Federal")
        state_df = get_tanf_df(file.path, state_sheets, year, column_dict, "State")

        federal.append(federal_df)
        state.append(state_df)

    line_tracker.export(os.path.join(diagnostics_dir, "LineSources.xlsx"))

    # Concatenate all years
    federal_df = pd.concat(federal)
    federal_df.set_index("year", append=True, inplace=True)

    state_df = pd.concat(state)
    state_df.set_index("year", append=True, inplace=True)

    for df in [state_df, federal_df]:
        validate_data_frame(df)

    validator = ExpenditureDataChecker(federal_df, "Federal", "196", "export")
    validator.check()
    validator.export(os.path.join(diagnostics_dir, "federal_checks_2010_2014.xlsx"))

    # Export
    if export:
        federal_df.to_csv(os.path.join(inter_dir, "federal_2010_2014.csv"))
        state_df.to_csv(os.path.join(inter_dir, "state_2010_2014.csv"))

        # Output list of lines missing from appended file
        instruction_file = os.path.join(input_dir, "Instruction Crosswalk.xlsx")
        sheet_name = "Missing Lines 2010-2014"
        writer = pd.ExcelWriter(
            instruction_file, engine="openpyxl", mode="a", if_sheet_exists="replace"
        )

        all_line_numbers = [
            standardize_line_number(line) for line in column_dict.keys()
        ]
        missing_columns = set(all_line_numbers) - (
            set(federal_df.columns).union(set(state_df.columns))
        )
        missing_columns = list(missing_columns)
        missing_columns.sort()
        pd.Series(missing_columns).to_excel(writer, sheet_name=sheet_name)

        writer.close()

        return None

    return federal_df, state_df


if __name__ == "__main__":
    main(export=True)
