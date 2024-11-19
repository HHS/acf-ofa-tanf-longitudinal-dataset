import os

import pandas as pd

from otld.paths import input_dir, inter_dir


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
        if not original:
            continue
        elif isinstance(original, str):
            new_df[revised] = df[original]
        elif isinstance(original, list):
            new_df[revised] = df[original].sum(axis=1)

    return new_df


def main():
    # Load crosswalk
    crosswalk = pd.read_excel(
        os.path.join(input_dir, "Instruction Crosswalk.xlsx"), sheet_name="crosswalk"
    )
    crosswalk.fillna("", inplace=True)
    crosswalk = crosswalk.astype(str)

    crosswalk_dict = {}
    for key, value in zip(crosswalk["196R"], crosswalk[196]):
        if isinstance(value, str):
            crosswalk_dict[key] = value.split(",") if value.find(",") > -1 else value
        elif pd.isna(value) or not value:
            crosswalk_dict[key] = None
        else:
            crosswalk_dict[key] = value

    columns_196 = get_column_list(crosswalk, 196)
    columns_196_r = get_column_list(crosswalk, "196R")

    files = os.listdir(inter_dir)
    federal = []
    state = []
    post_2015 = {}

    # Combine files before 2015
    for file in files:
        df = pd.read_csv(os.path.join(inter_dir, file), index_col=["STATE", "year"])
        level = "state" if file.startswith("state") else "federal"

        if file.find("2015_2023") > -1:
            post_2015[level] = df.filter(columns_196_r)
        elif level == "federal":
            federal.append(df.filter(columns_196))
        elif level == "state":
            state.append(df.filter(columns_196))

    state = pd.concat(state)
    federal = pd.concat(federal)

    # print(state)
    # print(federal)

    # Map columns across 2014/2015 disjunction
    # Append pre and post-2015

    return federal, state


if __name__ == "__main__":
    main()
