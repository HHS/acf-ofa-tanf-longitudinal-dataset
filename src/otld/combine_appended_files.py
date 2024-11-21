import os
import re

import pandas as pd

from otld.paths import inter_dir
from otld.utils.crosswalk_2014_2015 import crosswalk, crosswalk_dict


def get_column_list(crosswalk: pd.DataFrame, column: str | int):
    columns = crosswalk[column].dropna().to_list()
    columns = [str(c) for c in columns]
    columns = ",".join(columns)
    columns = columns.split(",")
    columns = [c.strip() for c in columns]

    return columns


def map_columns(df: pd.DataFrame, crosswalk_dict: dict):
    new_df = pd.DataFrame()
    for revised, original in crosswalk_dict.items():
        try:
            if not original:
                continue
            elif isinstance(original, str):
                new_df[revised] = df[original]
            elif isinstance(original, list):
                new_df[revised] = df[original].sum(axis=1)
        except:
            continue

    return new_df


def reorder_alpha_numeric(values: list | pd.Series) -> list:
    values = [re.search(r"(\d+)(\w*)", value).groups() for value in values]
    values = [(int(value[0]), value[1]) for value in values]
    values.sort()
    values = [(str(value[0]), value[1]) for value in values]
    values = ["".join(value) for value in values]

    return values


def main():
    columns_196 = get_column_list(crosswalk, 196)
    columns_196_r = get_column_list(crosswalk, "196R")

    files = os.listdir(inter_dir)
    federal = []
    state = []

    # Append files to relevant lists
    for file in files:
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
    state = pd.concat(state)
    state = state[reorder_alpha_numeric(state.columns)]
    federal = pd.concat(federal)
    federal = federal[reorder_alpha_numeric(federal.columns)]

    return federal, state


if __name__ == "__main__":
    main()
