"""Format appended files

This module formats appended TANF financial data.
"""

import os

import numpy as np
import pandas as pd

from otld.append import combine_appended_files
from otld.utils.openpyxl_utils import export_workbook


def format_pd_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Format pandas data frame columns.

    Apply transformations to column values.

    Args:
        df (pd.DataFrame): Data frame to format.

    Returns:
        pd.DataFrame: Formatted data frame.
    """
    numeric = df.select_dtypes(include=[np.number]).columns
    df[numeric] = df[numeric].map(lambda x: f"{x:,.0f}")

    return df


def main():
    """Entry point for script to format appended files"""

    frames = combine_appended_files.main()
    drop_columns = [
        "Basic Assistance",
        "Work, Education, & Training Activities",
        "Child Care (Spent or Transferred)",
        "Program Management",
        "Refundable Tax Credits",
        "Child Welfare Services",
        "Pre-Kindergarten/Head Start",
        "Transferred to SSBG",
        "Out-of-Wedlock Pregnancy Prevention",
        "Non-Recurrent Short Term Benefits",
        "Work Supports & Supportive Services",
        "Services for Children & Youth",
        "Authorized Solely Under Prior Law",
        "Fatherhood & Two-Parent Family Programs",
        "Other",
    ]

    export_workbook(
        frames, os.path.join(out_dir, "FinancialDataWide.xlsx"), drop_columns
    )

    frames["FinancialData"] = []
    for frame in frames:
        if frame == "FinancialData":
            continue
        frames[frame] = frames[frame].melt(
            var_name="Category", value_name="Amount", ignore_index=False
        )
        frames[frame]["Funding"] = frame
        frames["FinancialData"].append(frames[frame])

    frames["FinancialData"] = pd.concat(frames["FinancialData"])
    for frame in list(frames.keys()):
        if frame != "FinancialData":
            del frames[frame]

    export_workbook(
        frames, os.path.join(tableau_dir, "data", "FinancialDataLongRaw.xlsx")
    )

    frames["FinancialData"] = frames["FinancialData"][
        frames["FinancialData"].map(lambda x: x not in drop_columns)
    ]
    export_workbook(frames, os.path.join(out_dir, "FinancialDataLong.xlsx"))


if __name__ == "__main__":
    from otld.paths import out_dir, tableau_dir

    main()
