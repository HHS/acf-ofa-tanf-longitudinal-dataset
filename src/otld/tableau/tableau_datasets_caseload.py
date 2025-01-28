import math
import os

import pandas as pd
from openpyxl.styles.numbers import FORMAT_NUMBER_COMMA_SEPARATED1

from otld.paths import tableau_dir
from otld.utils import excel_to_dict, export_workbook, wide_with_index


def generate_wide_data():
    frames = excel_to_dict(os.path.join(tableau_dir, "CaseloadDataWideRaw.xlsx"))
    export_workbook(
        wide_with_index(frames, "CaseloadData"),
        os.path.join(tableau_dir, "data", "CaseloadDataWide.xlsx"),
        format_options={
            "skip_cols": 3,
            "number_format": FORMAT_NUMBER_COMMA_SEPARATED1,
        },
    )


def generate_long_data():
    df = pd.read_excel(os.path.join(tableau_dir, "data", "CaseloadDataLongRaw.xlsx"))
    df["log_value"] = df["Number"].map(
        lambda x: math.log(x) if isinstance(x, (float, int)) and x != 0 else None
    )
    df.to_excel(os.path.join(tableau_dir, "data", "CasleoadDataLong.xlsx"))


def main():
    generate_wide_data()
    generate_long_data()


if __name__ == "__main__":
    main()
