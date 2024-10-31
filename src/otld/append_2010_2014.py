import json
import os
import re

import openpyxl
import openpyxl.worksheet
import openpyxl.worksheet.worksheet
import pandas as pd

from otld.paths import input_dir, inter_dir
from otld.utils import delete_empty_columns, get_column_names

with open(os.path.join(input_dir, "column_dict_196.json"), "r") as file:
    column_dict = json.load(file)


def rename_columns(df: pd.DataFrame, sheet: str, column_dict: dict) -> pd.DataFrame:
    if sheet.endswith("Non-Assistance"):
        number = 6
    elif sheet.endswith("Assistance"):
        number = 5
    elif sheet.endswith("Non-A Subcategories"):
        number = 6
    else:
        raise ValueError("Invalid sheet")

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

    columns = ["STATE"]
    columns.extend(column_dict.keys())
    df.columns = columns

    return df


def get_tanf_df(
    tanf_path: str | os.PathLike, sheets: list[str], year: int
) -> pd.DataFrame:
    data = []
    for sheet in sheets:
        tanf_excel_file = openpyxl.load_workbook(tanf_path)
        tanf_df = tanf_excel_file[sheet]
        delete_empty_columns(tanf_df)
        columns, i = get_column_names(tanf_df)

        tanf_df = pd.read_excel(tanf_path, sheet_name=sheet, skiprows=i, header=None)
        tanf_df.columns = columns
        tanf_df = rename_columns(tanf_df, sheet, column_dict)

        # Clean up and add to data list
        tanf_df.dropna(subset=["STATE"], inplace=True)
        tanf_df.set_index("STATE", inplace=True)
        data.append(tanf_df)

    # Concatenate
    tanf_df = pd.concat(data, axis=1)
    tanf_df["year"] = year

    return tanf_df


def main():
    tanf_path = os.path.join(input_dir, "2010_2023")
    tanf_files = os.scandir(tanf_path)
    federal = []
    state = []
    sheets = ["Assistance", "Non-Assistance", "Non-A Subcategories"]
    fed_sheets = [f"Federal {sheet}" for sheet in sheets]
    state_sheets = [f"State {sheet}" for sheet in sheets]
    for file in tanf_files:
        file_year = re.search(r"(\d{4}).xlsx?", str(file.path)).group(1)
        file_year = int(file_year)
        if file_year >= 2015:
            continue

        federal_df = get_tanf_df(file.path, fed_sheets, file_year)
        state_df = get_tanf_df(file.path, state_sheets, file_year)
        federal.append(federal_df)
        state.append(state_df)

    federal_df = pd.concat(federal).reset_index()
    state_df = pd.concat(state).reset_index()

    federal_df.to_csv(os.path.join(inter_dir, "federal_2010_2014.csv"), index=False)
    state_df.to_csv(os.path.join(inter_dir, "state_2010_2014.csv"), index=False)


if __name__ == "__main__":
    main()
