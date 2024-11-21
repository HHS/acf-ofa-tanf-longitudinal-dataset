import os

import pandas as pd

from otld.paths import out_dir, scrap_dir
from otld.utils.crosswalk_2014_2015 import crosswalk_dict


def main():
    excel_file = os.path.join(out_dir, "Combined Data.xlsx")
    excel_file = pd.ExcelFile(excel_file)

    excel_writer = os.path.join(scrap_dir, "missingness.xlsx")
    if not os.path.exists(excel_writer):
        pd.DataFrame().to_excel(excel_writer, sheet_name="Federal")

    excel_writer = pd.ExcelWriter(
        excel_writer, engine="openpyxl", mode="a", if_sheet_exists="replace"
    )

    for level in ["Federal", "State"]:
        df = pd.read_excel(excel_file, level)
        df = df.set_index(["STATE", "year"])

        df_missing = df.groupby(["year"]).count()
        column_has_missing = df_missing.apply(lambda x: (x <= 1).any()).tolist()
        df_missing = df_missing.iloc[:, column_has_missing]

        missing_columns = df_missing.columns
        missing_columns = [
            column for column in missing_columns if crosswalk_dict[column]
        ]
        df_missing[missing_columns].to_excel(excel_writer, sheet_name=level, index=True)

    excel_writer.close()


if __name__ == "__main__":
    main()
