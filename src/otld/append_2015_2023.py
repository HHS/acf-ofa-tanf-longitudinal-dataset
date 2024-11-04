import json
import os
import re

import openpyxl
import pandas as pd
from fuzzywuzzy import fuzz, process

from otld.paths import input_dir, inter_dir
from otld.utils import delete_empty_columns, get_column_names, standardize_line_number

# Load column dictionary for 196 revised instructions
with open(os.path.join(input_dir, "column_dict_196_r.json"), "r") as file:
    column_dict = json.load(file)


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns of dataframe

    Rename columns of dataframe to line numbers.

    Args:
        df (pd.DataFrame): Dataframe to rename columns of

    Returns:
        pd.DataFrame: Dataframe with renamed columns
    """

    columns = df.columns.tolist()

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

        # If no match, choose column name based on position
        for i, column in enumerate(columns):
            if fuzzy_matches[i] == column_list[i]:
                renamer[column] = inverted_column_dict[fuzzy_matches[i][0]]
            elif fuzzy_matches[i] is not None and fuzzy_matches[i][1] == 100:
                renamer[column] = inverted_column_dict[fuzzy_matches[i][0]]
            else:
                renamer[column] = inverted_column_dict[column_list[i]]

    df.rename(columns=renamer, inplace=True)
    df.columns = df.columns.map(standardize_line_number)

    return df


def get_tanf_df(tanf_path: str | os.PathLike, sheet: str, year: int) -> pd.DataFrame:
    """Extract TANF data from Excel file

    Args:
        tanf_path (str | os.PathLike): Path to TANF Excel file
        sheet (str): Sheet name to extract data from
        year (int): Year of data

    Returns:
        pd.DataFrame: Extracted TANF data
    """

    # Load data and delete columns with no data
    tanf_excel_file = openpyxl.load_workbook(tanf_path)
    tanf_df = tanf_excel_file[sheet]
    delete_empty_columns(tanf_df)

    # Get column names and load data with pandas
    columns, i = get_column_names(tanf_df)
    tanf_df = pd.read_excel(tanf_path, sheet_name=sheet, skiprows=i, header=None)

    # Rename columns and add year
    tanf_df.columns = columns
    tanf_df = rename_columns(tanf_df)
    tanf_df["year"] = year

    return tanf_df


def main():
    """Entry point for appending 2015-2023"""

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

        federal.append(get_tanf_df(file.path, "C.1 Federal Expenditures", year))
        state.append(get_tanf_df(file.path, "C.2 State Expenditures", year))

    # Concatenate all years
    federal_df = pd.concat(federal)
    state_df = pd.concat(state)

    # Export
    federal_df.to_csv(os.path.join(inter_dir, "federal_2015_2023.csv"), index=False)
    state_df.to_csv(os.path.join(inter_dir, "state_2015_2023.csv"), index=False)


if __name__ == "__main__":
    main()
