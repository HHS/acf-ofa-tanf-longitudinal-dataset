"""Check combined workbook for missing columns"""

import os

import pandas as pd

from otld.paths import diagnostics_dir
from otld.utils.crosswalk_2014_2015 import crosswalk_dict


def main(frames: dict):
    """Check combined workbook for missing columns"""
    excel_writer = os.path.join(diagnostics_dir, "missingness.xlsx")
    if not os.path.exists(excel_writer):
        pd.DataFrame().to_excel(excel_writer, sheet_name="Federal")

    excel_writer = pd.ExcelWriter(
        excel_writer, engine="openpyxl", mode="a", if_sheet_exists="replace"
    )

    for level in ["Federal", "State"]:
        df = frames[level]

        df_missing = df.groupby(["year"]).count()
        column_has_missing = df_missing.apply(lambda x: (x <= 1).any()).tolist()
        df_missing = df_missing.iloc[:, column_has_missing]

        missing_columns = df_missing.columns
        missing_columns = [
            column for column in missing_columns if crosswalk_dict[column][196]
        ]
        df_missing[missing_columns].to_excel(excel_writer, sheet_name=level, index=True)

    excel_writer.close()


if __name__ == "__main__":
    main()
