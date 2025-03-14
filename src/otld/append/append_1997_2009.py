"""Append Excel workbooks for 1997-2009"""

import json
import os
import re

import pandas as pd

from otld.paths import diagnostics_dir, input_dir, inter_dir
from otld.utils import (
    FinancialDataChecker,
    convert_to_numeric,
    standardize_file_name,
    standardize_line_number,
    validate_data_frame,
)
from otld.utils.financial_utils import reindex_state_year
from otld.utils.LineTracker import LineTracker

# Instantiate a LineTracker object to track what files lines came from.
line_tracker = LineTracker()


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
        name = re.search(r"Line\s*(.+)", name, re.IGNORECASE).group(1)
        name = standardize_line_number(name)

    return name


def get_relevant_columns(book: str, sheet: str) -> list[str]:
    """Select the relevant columns given a path and sheet

    Args:
        book (str): Excel workbook name.
        sheet (str): Excel worksheet name.

    Returns:
        list[str]: Returns a list of relevant columns. Returns None if
        all columns should be kept.
    """
    sheet = sheet.replace(" ", "").lower()

    if book.startswith("table_a_combined") and (
        sheet == "a-1" or sheet == "spendingfromfedltanfgrantinfy"
    ):
        columns = ["5", "6", "7", "9", "10"]
    elif re.match(r"\d{4}", sheet) or sheet == "spendingfromfedltanfgrantinfy":
        columns = ["1", "2", "3", "4"]
    elif book.startswith("table_a1") and sheet == "a1-1":
        columns = ["1", "2", "3", "4"]
    elif sheet == "combinedspend":
        columns = ["5", "6", "7", "9", "10"]
    else:
        return None

    return columns


def get_tanf_df(paths: list[str], year: int) -> tuple[pd.DataFrame]:
    """Get data from TANF Financial files

    Args:
        paths (list[str]): List of paths to Excel workbooks.
        year (int): The year associated with the Excel workbooks.

    Returns:
       tuple[pd.DataFrame]: Appended workbooks as data frames.
    """
    state = []
    federal = []

    for path in paths:
        # Extract stem from path
        path_stem = os.path.split(path)[1]
        path_stem_std = standardize_file_name(path_stem)

        # Load file and get sheets
        tanf_excel_file = pd.ExcelFile(path)
        sheets = tanf_excel_file.sheet_names
        data = []

        # Get level that this path applies to
        level = (
            "State"
            if re.search(r"table\s*[bc]\s?(latest)?", path, re.IGNORECASE)
            else "Federal"
        )

        # Add year to sources dictionary
        if year not in line_tracker.sources:
            line_tracker.sources[year] = []

        for sheet in sheets:
            if sheet.startswith("Footnotes"):
                continue
            elif re.match(r"\d{4}", path_stem_std) and not sheet.endswith("spend"):
                continue
            elif re.match(r"table_a1_", path_stem_std) and not (
                sheet.startswith("Spending") or sheet.startswith("A1-1")
            ):
                continue

            # Begin building tracker dictionary
            tracker = {"FileName": path_stem, "SheetName": sheet, "Level": level}

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

            # Rename columns and keep only rows after column row
            tanf_df.columns = tanf_df.iloc[i]
            tanf_df = tanf_df.iloc[i + 1 :, :].copy()

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
            tanf_df = tanf_df.filter(regex=r"^\s*L[iI][nN][eE]")
            tanf_df = tanf_df.dropna(axis=0, how="all")

            # Rename columns
            tracker["BaseColumns"] = tanf_df.columns.to_list()
            tanf_df = tanf_df.rename(rename_columns, axis=1)
            tracker["RenamedColumns"] = tanf_df.columns.to_list()

            assert len(tracker["BaseColumns"]) == len(tracker["RenamedColumns"])
            tracker["Columns"] = {
                renamed: base
                for renamed, base in zip(
                    tracker["RenamedColumns"], tracker["BaseColumns"]
                )
            }
            # Convert columns to integer
            tanf_df = tanf_df.map(
                lambda x: 0 if type(x) is str and x.strip() == "-" else x
            )
            tanf_df = tanf_df.apply(convert_to_numeric)
            tanf_df.fillna(0, inplace=True)

            # Select columns
            columns = get_relevant_columns(path_stem_std, sheet)
            if columns:
                tanf_df = tanf_df[columns]
            else:
                columns = tanf_df.columns.to_list()

            tracker["BaseColumns"] = [tracker["Columns"][column] for column in columns]
            tracker["RenamedColumns"] = columns
            del tracker["Columns"]

            line_tracker.sources[year].append(tracker)

            data.append(tanf_df)

        # Concatenate data frames and remove duplicated columns
        tanf_df = pd.concat(data, axis=1)
        tanf_df = tanf_df.loc[:, ~tanf_df.columns.duplicated()]

        # Determine whether the data frame is state or federal
        if level == "State":
            state.append(tanf_df)
        else:
            federal.append(tanf_df)

    # Add state MOE files
    state = state[0].add(state[1], level=0)

    # Concatenate federal files
    federal = pd.concat(federal, axis=1)

    # Add year column
    state["year"] = year
    federal["year"] = year

    return federal, state


def get_tanf_files(directory: str, year: int) -> list[str]:
    """Choose the workbooks to extract data from.

    Args:
        directory (str): The directory to search for Excel workbooks.
        year (int): The year the directory contains data for.

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
            r"table_a1_.*_in_fy_\d+(_through_the_fourth_quarter)?.xls",
            clean_file,
        )

        table_b_c_condition = (
            clean_file.find("table_b") > -1 or clean_file.find("table_c") > -1
        )
        combined_table_condition = (
            clean_file.find("a_combined") > -1 or clean_file.startswith("combined")
        ) and not clean_file.endswith("arra.xls")

        year_latest_condition = clean_file.startswith(f"{year}")

        latest_table_condition = re.search(r"table[abc]latest", clean_file)

        if (
            table_a_condition
            or table_b_c_condition
            or combined_table_condition
            or latest_table_condition
            or year_latest_condition
        ):
            files.append(os.path.join(tanf_files[0], file))
        else:
            continue

    assert len(files) == 4, "Incorrect number of files"
    return files


def add_us_total(df: pd.DataFrame) -> pd.DataFrame:
    """Add U.S. total row.

    Args:
        df (pd.DataFrame): Data frame to add total row to

    Returns:
        pd.DataFrame: Data frame with total row
    """
    us_total = df.groupby("year").sum().reset_index()
    us_total.index = ["U.S. TOTAL" for i in range(us_total.shape[0])]
    us_total.index.name = "STATE"
    df = pd.concat([df, us_total])

    return df


def gen_carryover(df: pd.DataFrame) -> pd.DataFrame:
    """Generate carryover

    Carryover is generated by summing federal unliquidated obligations and
    unobligated balance in the prior year.

    Args:
        df (pd.DataFrame): Dataframe for which to generate carryover.

    Returns:
        pd.DataFrame: Dataframe with carryover.
    """

    def carryover(row: pd.Series):
        index = (row.name[0], row.name[1] - 1)
        try:
            carryover = df.loc[index, ["9", "10"]].sum()
        except KeyError:
            carryover = 0

        return carryover

    df["Carryover"] = df.apply(lambda row: carryover(row), axis=1)

    return df


def main(export: bool = False) -> tuple[pd.DataFrame]:
    """Entry point for appending years 1997-2009

    Args:
        export (bool): Export csv versions of the data frames.

    Returns:
        tuple[pd.DataFrame]: Federal and state appended data frames for 1997-2009
    """

    # Load column dictionary for 196 instructions
    with open(os.path.join(input_dir, "column_dict_196.json"), "r") as file:
        column_dict = json.load(file)  # noqa

    # Select directories
    tanf_dirs = list(range(1997, 2010))
    tanf_dirs = [os.path.join(input_dir, str(directory)) for directory in tanf_dirs]
    federal = []
    state = []

    # Loop through directories and get data
    for directory in tanf_dirs:
        year = re.search(r"(\d{4})$", directory).group(1)
        year = int(year)

        files = get_tanf_files(directory, year)
        federal_df, state_df = get_tanf_df(files, year)

        federal.append(federal_df)
        state.append(state_df)

    # Concatenate all years
    federal_df = pd.concat(federal)
    if "U.S. TOTAL" not in federal_df.index:
        federal_df = add_us_total(federal_df)

    federal_df.set_index("year", append=True, inplace=True)
    federal_df = reindex_state_year(federal_df)
    federal_df = gen_carryover(federal_df)

    state_df = pd.concat(state)
    if "U.S. TOTAL" not in state_df.index:
        state_df = add_us_total(state_df)

    state_df.set_index("year", append=True, inplace=True)
    state_df = reindex_state_year(state_df)

    # Validation
    for df in [federal_df, state_df]:
        validate_data_frame(df)

    validator = FinancialDataChecker(federal_df, "Federal", "196", "export")
    validator.check()
    validator.export(os.path.join(diagnostics_dir, "federal_checks_1997_2009.xlsx"))

    # Export
    line_tracker.export(os.path.join(diagnostics_dir, "LineSources.xlsx"))
    if export:
        federal_df.to_csv(os.path.join(inter_dir, "federal_1997_2009.csv"))
        state_df.to_csv(os.path.join(inter_dir, "state_1997_2009.csv"))
        return None

    return federal_df, state_df


if __name__ == "__main__":
    main(export=True)
