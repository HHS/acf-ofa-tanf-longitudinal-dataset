"""Append Excel workbooks for 1997-2009"""

import json
import os
import re

import pandas as pd

from otld.paths import input_dir, inter_dir
from otld.utils import standardize_file_name, standardize_line_number

# Load column dictionary for 196 instructions
with open(os.path.join(input_dir, "column_dict_196.json"), "r") as file:
    column_dict = json.load(file)


def rename_columns(name: str) -> str:
    """Rename columns

    Rename data frame columns to only numbers.

    Args:
        name (str): Original column name.

    Returns:
        str: New column name.
    """
    if name == "STATE":
        pass
    else:
        name = re.search(r"Line\s*(.+)", name).group(1)
        name = standardize_line_number(name)

    return name


def make_negative_string(string: str) -> str:
    """Make negative string

    Convert a string to a negative string.

    Args:
        x (str): String to convert.

    Returns:
        str: Negative string.
    """
    string = re.sub(r"\<|\(", "-", string)
    string = re.sub(r"\>|\)|\,", "", string)
    return string


def convert_to_int(series: pd.Series) -> pd.Series:
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
        series = series.astype(int)
    except:
        raise

    return series


def get_tanf_df(paths: list[str], year: int) -> tuple[pd.DataFrame]:
    """Get data from TANF Financial files

    Args:
        paths (list[str]): List of paths to Excel workbooks.
        year (int): The year associated with the Excel workbooks.

    Returns:
       tuple[pd.DataFrame]: Appended workbooks as data frames.
    """
    state = []

    for path in paths:
        # Load file and get sheets
        tanf_excel_file = pd.ExcelFile(path)
        sheets = tanf_excel_file.sheet_names
        data = []
        for sheet in sheets:
            if sheet.startswith("Footnotes"):
                continue

            # Load data
            tanf_df = pd.read_excel(tanf_excel_file, sheet_name=sheet, header=None)

            # Find the row with column names
            i = 0
            columns = tanf_df.iloc[i].map(
                lambda x: re.search(r"^\s*Line", x) if type(x) is str else None
            )
            while not columns.any():
                i += 1
                columns = tanf_df.iloc[i].map(
                    lambda x: re.search(r"^\s*Line", x) if type(x) is str else None
                )

            tanf_df.columns = tanf_df.iloc[i]
            tanf_df = tanf_df.iloc[i + 1 :]

            # Drop if column is fully NA
            tanf_df.dropna(axis=1, how="all", inplace=True)
            columns = list(tanf_df.columns)

            # Drop if STATE is an invalid value or NAs
            if columns[0] != "STATE":
                columns[0] = "STATE"
                tanf_df.columns = columns

            tanf_df.dropna(subset=["STATE"], inplace=True)
            tanf_df = tanf_df[
                tanf_df["STATE"].map(
                    lambda x: not bool(
                        re.search(r"state|total|percentage", x, re.IGNORECASE)
                    )
                )
            ]

            # Remove NAs and set index to state
            tanf_df["STATE"] = tanf_df["STATE"].apply(lambda x: x.strip())
            tanf_df.set_index("STATE", inplace=True)
            tanf_df = tanf_df.filter(regex="^\s*Line")
            tanf_df = tanf_df.dropna(axis=0, how="all")
            tanf_df.fillna("0", inplace=True)

            # Rename columns
            tanf_df = tanf_df.rename(rename_columns, axis=1)

            # Convert columns to integer
            tanf_df = tanf_df.map(
                lambda x: 0 if type(x) is str and x.strip() == "-" else x
            )
            tanf_df = tanf_df.apply(convert_to_int)

            data.append(tanf_df)

        # Concatenate data frames and remove duplicated columns
        tanf_df = pd.concat(data, axis=1)
        tanf_df = tanf_df.loc[:, ~tanf_df.columns.duplicated()]

        # Determine whether the data frame is state or federal
        if re.search(r"table\s*[bc]\s?(latest)?", path, re.IGNORECASE):
            state.append(tanf_df)
        else:
            federal = tanf_df

    # Add state MOE files
    state = state[0].add(state[1], level=0)

    # Add year column
    state["year"] = year
    federal["year"] = year

    return federal, state


def get_tanf_files(directory: str) -> list[str]:
    """Choose the workbooks to extract data from.

    Args:
        directory (str): The directory to search for Excel workbooks.

    Returns:
        list[str]: A list of paths to Excel workbooks.
    """

    # Walk directory for TANF files
    tanf_file_generator = os.walk(directory)
    tanf_files = next(tanf_file_generator)
    while not tanf_files[2]:
        tanf_files = next(tanf_file_generator)
    files = []

    # Identify the relevant workbooks
    for file in tanf_files[2]:
        clean_file = standardize_file_name(file)
        table_a_condition = re.search(
            r"table_a.*_combined.*_in_fy_\d+(_through_the_fourth_quarter)?.xls",
            clean_file,
        )
        table_b_c_condition = (
            clean_file.find("table_b") > -1 or clean_file.find("table_c") > -1
        )
        combined_table_condition = clean_file.startswith("combined")
        latest_table_condition = re.search(r"table[abc]latest", clean_file)

        if (
            table_a_condition
            or table_b_c_condition
            or combined_table_condition
            or latest_table_condition
        ):
            files.append(os.path.join(tanf_files[0], file))
        else:
            continue

    assert len(files) == 3, "Incorrect number of files"
    return files


def main():
    """Entry point for appending years 2006-2009"""

    # Select directories
    tanf_dirs = list(range(1997, 2010))
    tanf_dirs = [os.path.join(input_dir, str(directory)) for directory in tanf_dirs]
    federal = []
    state = []

    # Loop through directories and get data
    for directory in tanf_dirs:
        year = re.search(r"(\d{4})$", directory).group(1)
        year = int(year)

        files = get_tanf_files(directory)
        federal_df, state_df = get_tanf_df(files, year)

        federal.append(federal_df)
        state.append(state_df)

    # Concatenate all years
    federal_df = pd.concat(federal)
    state_df = pd.concat(state)

    # Export
    federal_df.to_csv(os.path.join(inter_dir, "federal_1997_2009.csv"))
    state_df.to_csv(os.path.join(inter_dir, "state_1997_2009.csv"))


if __name__ == "__main__":
    main()
