"""Format appended files

This module formats appended TANF financial data.
"""

import os

import numpy as np
import pandas as pd

from otld import combine_appended_files
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
    export_workbook(frames, os.path.join(out_dir, "FinancialDataWide.xlsx"))

    frames["FinancialData"] = []
    for frame in frames:
        if frame == "FinancialData":
            continue
        frames[frame] = frames[frame].melt(
            var_name="Category", value_name="Amount", ignore_index=False
        )
        frames[frame]["Level"] = frame
        frames["FinancialData"].append(frames[frame])

    frames["FinancialData"] = pd.concat(frames["FinancialData"])
    for frame in list(frames.keys()):
        if frame != "FinancialData":
            del frames[frame]

    export_workbook(frames, os.path.join(out_dir, "FinancialDataLong.xlsx"))


if __name__ == "__main__":
    from otld.paths import out_dir

    main()
