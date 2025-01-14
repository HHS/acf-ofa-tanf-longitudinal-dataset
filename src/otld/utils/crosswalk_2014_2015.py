"""Create crosswalk for mapping across 2014-2015 disjunction"""

import os
import sys

import pandas as pd

from otld.paths import input_dir

try:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        input_dir = os.path.join(os.path.dirname(__file__), "..", "..")

    crosswalk = pd.read_excel(
        os.path.join(input_dir, "Instruction Crosswalk.xlsx"), sheet_name="crosswalk"
    )

    crosswalk.fillna("", inplace=True)
    crosswalk = crosswalk.astype(str)

    crosswalk_dict = crosswalk.set_index(["196R"]).to_dict(orient="index")
    for key in crosswalk_dict:
        value_196 = crosswalk_dict[key][196]
        if isinstance(value_196, str):
            crosswalk_dict[key][196] = (
                value_196.split(",") if value_196.find(",") > -1 else value_196
            )
        elif pd.isna(value_196) or not value_196:
            crosswalk_dict[key][196] = None
        else:
            crosswalk_dict[key][196] = value_196
except FileNotFoundError:
    crosswalk = pd.DataFrame()
    crosswalk_dict = {}


def map_columns(df: pd.DataFrame, crosswalk_dict: dict) -> pd.DataFrame:
    """Convert ACF-196 columns into ACF-196R equivalents.

    Args:
        df (pd.DataFrame): Data frame in which to make conversion.
        crosswalk_dict (dict): Dictionary mapping ACF-196 to ACF-196R

    Returns:
        pd.DataFrame: Data frame with columns converted to ACF-196R equivalents
    """
    new_df = pd.DataFrame()
    for key, value in crosswalk_dict.items():
        value_196 = value[196]
        try:
            if not value_196:
                continue
            # If values is a string, rename
            elif isinstance(value_196, str):
                new_df[key] = df[value_196]
            # Otherwise, sum the two columns
            elif isinstance(value_196, list):
                new_df[key] = df[value_196].sum(axis=1)
        except KeyError:
            continue

    return new_df
