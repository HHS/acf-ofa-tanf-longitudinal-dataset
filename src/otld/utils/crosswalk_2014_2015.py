"""Create crosswalk for mapping across 2014-2015 disjunction"""

import os

import pandas as pd

from otld.paths import input_dir

try:
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
    pass
