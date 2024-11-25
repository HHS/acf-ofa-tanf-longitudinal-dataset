"""This module combines appended files across the 2014-2015 disjunction."""

import os
import re

import pandas as pd

from otld.paths import inter_dir
from otld.utils import missingness, reindex_state_year
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
    for key, value in crosswalk_dict.items():
        value_196 = value[196]
        try:
            if not value_196:
                continue
            elif isinstance(value_196, str):
                new_df[key] = df[value_196]
            elif isinstance(value_196, list):
                new_df[key] = df[value_196].sum(axis=1)
        except KeyError:
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
    rename_dict = {key: value["name"] for key, value in crosswalk_dict.items()}

    state = pd.concat(state)
    state = state[reorder_alpha_numeric(state.columns)]
    state.drop(["1", "2", "3", "4", "5", "7", "8", "24"], inplace=True, axis=1)

    federal = pd.concat(federal)
    federal = federal[reorder_alpha_numeric(federal.columns)]
    for df in [federal, state]:
        df.fillna(0, inplace=True)

    frames = {"Federal": federal, "State": state}

    missingness.main(frames)

    total = federal.add(state, fill_value=0)
    total.sort_index(level=["year", "STATE"], inplace=True)
    total = reindex_state_year(total)
    total = total[reorder_alpha_numeric(total.columns)]

    for df in [total, federal, state]:
        df.rename(columns=rename_dict, inplace=True)
        df.index.rename(["State", "Year"], inplace=True)

    frames.update({"Total": total})

    return frames


if __name__ == "__main__":
    main()
