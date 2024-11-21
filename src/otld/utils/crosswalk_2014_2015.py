import os

import pandas as pd

from otld.paths import input_dir

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
