import json
import os
import re

import pandas as pd
import xlrd

from otld.paths import input_dir, inter_dir
from otld.utils import standardize_name

with open(os.path.join(input_dir, "column_dict_196.json"), "r") as file:
    column_dict = json.load(file)


def rename_columns(name: str) -> str:
    if name == "STATE":
        pass
    else:
        name = re.search(r"Line\s*(.+)", name).group(1)
        name = name.replace(" ", "")

    return name


def convert_to_int(series: pd.Series) -> int:
    try:
        series = series.map(
            lambda x: (
                x.replace("<", "-").replace(">", "").replace(",", "")
                if type(x) is str
                else x
            )
        )
        series = series.astype(int)
    except:
        raise

    return series


def get_tanf_df(paths: list[str], year: int) -> pd.DataFrame:
    state = []

    for path in paths:
        tanf_excel_file = pd.ExcelFile(path)
        sheets = tanf_excel_file.sheet_names
        data = []
        for sheet in sheets:
            if sheet.startswith("Footnotes"):
                continue

            # Determine rows to skip
            if year == 2009:
                if sheet == "A-1":
                    skip = 2
                else:
                    skip = 3
            else:
                skip = 4

            # Load data
            tanf_df = pd.read_excel(tanf_excel_file, sheet_name=sheet, skiprows=skip)
            tanf_df.dropna(axis=1, how="all", inplace=True)
            columns = list(tanf_df.columns)
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
            tanf_df.dropna(axis=1)
            tanf_df.set_index("STATE", inplace=True)
            tanf_df = tanf_df.filter(regex="^\s*Line")
            tanf_df = tanf_df.dropna(axis=0, how="all")

            # Rename columns
            tanf_df = tanf_df.rename(rename_columns, axis=1)

            # Convert columns to integer
            tanf_df = tanf_df.map(
                lambda x: 0 if type(x) is str and x.strip() == "-" else x
            )
            tanf_df = tanf_df.apply(convert_to_int)

            # Remove duplicated columns
            ~ tanf_df = tanf_df[not tanf_df.columns.duplicated()]

            data.append(tanf_df)

        tanf_df = pd.concat(data, axis=1)
        if re.search(r"\sB\s|\sC\s", path):
            state.append(tanf_df)
        else:
            federal = tanf_df

    # Concatenate
    state = state[0].add(state[1], level=0)
    state["year"] = year
    federal["year"] = year

    return federal, state


def get_tanf_files(directory: str) -> list[str]:
    tanf_files = os.walk(directory)
    tanf_files = next(tanf_files)
    files = []
    for file in tanf_files[2]:
        clean_file = standardize_name(file)
        if re.search(r"table_a.*_combined.*_in_fy_\d+.xls", clean_file):
            files.append(os.path.join(tanf_files[0], file))
        elif clean_file.find("table_b") > -1 or clean_file.find("table_c") > -1:
            files.append(os.path.join(tanf_files[0], file))

    assert len(files) == 3, "Incorrect number of files"
    return files


def main():
    tanf_dirs = list(range(2006, 2010))
    tanf_dirs = [os.path.join(input_dir, str(directory)) for directory in tanf_dirs]
    federal = []
    state = []
    for directory in tanf_dirs:
        year = re.search(r"(\d{4})$", directory).group(1)
        year = int(year)
        files = get_tanf_files(directory)
        federal_df, state_df = get_tanf_df(files, year)
        federal.append(federal_df)
        state.append(state_df)

    federal_df = pd.concat(federal)
    state_df = pd.concat(state)

    exit()
    # Export


if __name__ == "__main__":
    main()
