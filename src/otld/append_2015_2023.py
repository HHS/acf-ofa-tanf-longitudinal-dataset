"""Append Excel workbooks for 2015-2023"""

import json
import os
import re

import openpyxl
import pandas as pd
from fuzzywuzzy import fuzz, process

from otld.paths import diagnostics_dir, input_dir, inter_dir
from otld.utils import (
    convert_to_numeric,
    delete_empty_columns,
    get_column_names,
    standardize_line_number,
    validate_data_frame,
)
from otld.utils.LineTracker import LineTracker

line_tracker = LineTracker()


def rename_columns(df: pd.DataFrame, column_dict: dict, tracker: dict) -> pd.DataFrame:
    """Rename columns of dataframe.

    Rename columns of dataframe to line numbers.

    Args:
        df (pd.DataFrame): Dataframe to rename columns of.
        column_dict (dict): Dictionary mapping line numbers to field names.
        tracker (dict): Dictionary tracking column names before and after renaming.

    Returns:
        pd.DataFrame: Dataframe with renamed columns.
    """

    columns = df.columns.tolist()
    tracker["BaseColumns"] = columns.copy()

    # Remove state
    columns.pop(0)

    # Swap keys and values in column_dict
    inverted_column_dict = {value: key for key, value in column_dict.items()}

    # Decide how to assign new column names
    numbers = [re.match(r"(\d[\w\.]+?)\s", column) for column in columns]

    # If column names have numbers, extract them and use to match
    if all(numbers):
        numbers = [match.group(1).replace(".", "") for match in numbers]
        renamer = {columns[i]: number for i, number in enumerate(numbers)}
    else:
        # Use fuzzy matching
        column_list = list(column_dict.values())
        fuzzy_matches = [
            process.extractOne(column, column_list, scorer=fuzz.ratio, score_cutoff=80)
            for column in columns
        ]

        renamer = {}

        for i, column in enumerate(columns):
            # If match and column at position are identical, use match
            if fuzzy_matches[i] == column_list[i]:
                renamer[column] = inverted_column_dict[fuzzy_matches[i][0]]
            # If there is a perfect match, use match
            elif fuzzy_matches[i] is not None and fuzzy_matches[i][1] == 100:
                renamer[column] = inverted_column_dict[fuzzy_matches[i][0]]
            # Otherwise, use column at the current position
            else:
                renamer[column] = inverted_column_dict[column_list[i]]

    df.rename(columns=renamer, inplace=True)
    df.columns = df.columns.map(standardize_line_number)
    tracker["RenamedColumns"] = df.columns.to_list()

    return df


def get_tanf_df(
    tanf_path: str | os.PathLike, sheet: str, year: int, column_dict: dict, level: str
) -> pd.DataFrame:
    """Extract TANF data from Excel file

    Args:
        tanf_path (str | os.PathLike): Path to TANF Excel file
        sheet (str): Sheet name to extract data from
        year (int): Year of data
        column_dict (dict): Dictionary mapping line numbers to field names.
        level (str): Level of data: "State" or "Federal".

    Returns:
        pd.DataFrame: Extracted TANF data
    """
    path_stem = os.path.split(tanf_path)[1]
    tracker = {"FileName": path_stem, "SheetName": sheet, "Level": level}

    # Load data and delete columns with no data
    tanf_excel_file = openpyxl.load_workbook(tanf_path)
    tanf_df = tanf_excel_file[sheet]
    delete_empty_columns(tanf_df)

    # Get column names and load data with pandas
    columns, i = get_column_names(tanf_df)
    tanf_df = pd.read_excel(tanf_path, sheet_name=sheet, skiprows=i, header=None)

    # Rename columns and add year
    tanf_df.columns = columns
    tanf_df = rename_columns(tanf_df, column_dict, tracker)
    assert len(tracker["BaseColumns"]) == len(tracker["RenamedColumns"])

    # Set state as index
    tanf_df.dropna(subset=["STATE"], inplace=True)
    tanf_df["STATE"] = tanf_df["STATE"].map(lambda x: x.strip())
    tanf_df.set_index("STATE", inplace=True)

    # Convert to numeric
    tanf_df = tanf_df.apply(convert_to_numeric)
    tanf_df.fillna(0, inplace=True)

    # Add year column
    tanf_df["year"] = year

    line_tracker.sources[year].append(tracker)

    return tanf_df


def main(export: bool = False) -> tuple[pd.DataFrame]:
    """Entry point for appending 2015-2023

    Args:
        export (bool): Export csv versions of the data frames.

    Returns:
        tuple[pd.DataFrame]: Federal and state appended data frames for 1997-2009

    """

    # Load column dictionary for 196 revised instructions
    with open(os.path.join(input_dir, "column_dict_196_r.json"), "r") as file:
        column_dict = json.load(file)  # noqa

    # Select TANF files from 2015-2023
    tanf_path = os.path.join(input_dir, "2010_2023")
    tanf_files = os.scandir(tanf_path)
    federal = []
    state = []

    for file in tanf_files:
        # Extract year
        year = re.search(r"(\d{4}).xlsx?", str(file.path)).group(1)
        year = int(year)
        if year < 2015:
            continue

        line_tracker.sources[year] = []
        federal.append(
            get_tanf_df(
                file.path, "C.1 Federal Expenditures", year, column_dict, "Federal"
            )
        )
        state.append(
            get_tanf_df(file.path, "C.2 State Expenditures", year, column_dict, "State")
        )

    line_tracker.export(os.path.join(diagnostics_dir, "LineSources.xlsx"))

    # Concatenate all years
    federal_df = pd.concat(federal)
    federal_df.set_index("year", append=True, inplace=True)

    state_df = pd.concat(state)
    state_df.set_index("year", append=True, inplace=True)

    for df in [state_df, federal_df]:
        validate_data_frame(df)

    # Export
    if export:
        federal_df.to_csv(os.path.join(inter_dir, "federal_2015_2023.csv"))
        state_df.to_csv(os.path.join(inter_dir, "state_2015_2023.csv"))
        return None

    return federal_df, state_df


if __name__ == "__main__":
    main(export=True)
