import json
import os
import re

import openpyxl
import openpyxl.worksheet
import openpyxl.worksheet.worksheet
import pandas as pd
from fuzzywuzzy import fuzz, process

from otld.paths import input_dir, inter_dir
from otld.utils import delete_empty_columns, get_column_names

with open(os.path.join(input_dir, "column_dict_196_r.json"), "r") as file:
    column_dict = json.load(file)


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    columns = df.columns.tolist()
    # Remove state
    columns.pop(0)
    inverted_column_dict = {value: key for key, value in column_dict.items()}

    # Decide how to assign new column names
    numbers = [re.match(r"(\d[\w\.]+?)\s", column) for column in columns]
    # If column names have numbers, extract them and use to match
    if all(numbers):
        numbers = [match.group(1).replace(".", "") for match in numbers]
        renamer = {columns[i]: number for i, number in enumerate(numbers)}
    else:
        # Use fuzzy matching, if no match, choose based on position
        column_list = list(column_dict.values())
        fuzzy_matches = [
            process.extractOne(column, column_list, scorer=fuzz.ratio, score_cutoff=80)
            for column in columns
        ]
        renamer = {}
        for i, column in enumerate(columns):
            if fuzzy_matches[i] == column_list[i]:
                renamer[column] = inverted_column_dict[fuzzy_matches[i][0]]
            elif fuzzy_matches[i] is not None and fuzzy_matches[i][1] == 100:
                renamer[column] = inverted_column_dict[fuzzy_matches[i][0]]
            else:
                renamer[column] = inverted_column_dict[column_list[i]]

    df.rename(columns=renamer, inplace=True)

    return df


def get_tanf_df(tanf_path: str | os.PathLike, sheet: str, year: int) -> pd.DataFrame:
    tanf_excel_file = openpyxl.load_workbook(tanf_path)
    tanf_df = tanf_excel_file[sheet]
    delete_empty_columns(tanf_df)
    columns, i = get_column_names(tanf_df)
    tanf_df = pd.read_excel(tanf_path, sheet_name=sheet, skiprows=i, header=None)
    tanf_df.columns = columns
    tanf_df = rename_columns(tanf_df)
    tanf_df["year"] = year

    return tanf_df


def main():
    tanf_path = os.path.join(input_dir, "2010_2023")
    tanf_files = os.scandir(tanf_path)
    federal = []
    state = []
    for file in tanf_files:
        file_year = re.search(r"(\d{4}).xlsx?", str(file.path)).group(1)
        file_year = int(file_year)
        if file_year < 2015:
            continue
        federal.append(get_tanf_df(file.path, "C.1 Federal Expenditures", file_year))
        state.append(get_tanf_df(file.path, "C.2 State Expenditures", file_year))

    federal_df = pd.concat(federal)
    state_df = pd.concat(state)

    federal_df.to_csv(os.path.join(inter_dir, "federal_2015_2023.csv"), index=False)
    state_df.to_csv(os.path.join(inter_dir, "state_2015_2023.csv"), index=False)


if __name__ == "__main__":
    main()
