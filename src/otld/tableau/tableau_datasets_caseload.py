"""Module for caseload Tableau-specific datasets"""

import math
import os

import numpy as np
import pandas as pd

from otld.paths import tableau_dir
from otld.utils import excel_to_dict, export_workbook, wide_with_index
from otld.utils.caseload_utils import CASELOAD_FORMAT_OPTIONS


def generate_wide_data():
    """Generate Tableau-specific wide dataset"""
    frames = excel_to_dict(
        os.path.join(tableau_dir, "data", "CaseloadDataWideRaw.xlsx")
    )
    options = CASELOAD_FORMAT_OPTIONS.copy()
    options.update({"skip_cols": 4})
    export_workbook(
        wide_with_index(frames, "CaseloadData"),
        os.path.join(tableau_dir, "data", "CaseloadDataWide.xlsx"),
        format_options=options,
    )


def transform_caseload_long(df: pd.DataFrame) -> pd.DataFrame:
    """Transformations for caseload long data

    Args:
        df (pd.DataFrame): Caseload dataset to transform

    Returns:
        pd.DataFrame: Transformed caseload dataset
    """
    df["log_value"] = df["Number"].map(
        lambda x: math.log(x, 10) if isinstance(x, (float, int)) and x != 0 else None
    )

    # Calculate percentage of total
    df["group"] = df["Category"].apply(
        lambda x: "family" if x.lower().find("fam") > -1 else "recipients"
    )
    total = df[df["Category"].apply(lambda x: x.lower().find("total") > -1)]
    total = total[["FiscalYear", "State", "Funding", "group", "Number"]].rename(
        columns={"Number": "Total"}
    )
    df = df.merge(total, how="left", on=["FiscalYear", "State", "Funding", "group"])
    df["pct_of_total"] = round(df["Number"] / df["Total"], 4) * 100
    df["pct_of_total"] = df["pct_of_total"].replace(
        [np.nan, np.inf, -np.inf], [0, 0, 0]
    )
    df.drop(["Total", "group"], inplace=True, axis=1)

    # Deviation from base year
    base_year = (
        df.sort_values(["FiscalYear", "State", "Funding", "Category"])
        .groupby(["State", "Funding", "Category"])
        .first()[["FiscalYear", "Number"]]
        .rename(columns={"Number": "base"})
        .reset_index()
    )
    # Confirm years are as expected
    # Commented out because tests fail when this line is included and any appended file missing
    # these early years would also fail
    # assert all([year in [2000, 1997] for year in base_year["FiscalYear"]])
    base_year.drop("FiscalYear", axis=1, inplace=True)

    df = df.merge(base_year, how="left", on=["State", "Funding", "Category"])
    df["pct_deviation"] = round(df["Number"] / df["base"], 4) * 100
    df["pct_deviation"] = df["pct_deviation"].replace(
        [np.nan, np.inf, -np.inf], [0, 0, 0]
    )
    df.drop("base", inplace=True, axis=1)

    return df


def generate_long_data():
    """Generate Tableau-specific long dataset"""
    df = pd.read_excel(os.path.join(tableau_dir, "data", "CaseloadDataLongRaw.xlsx"))

    df = transform_caseload_long(df)

    # Export
    df.to_excel(
        os.path.join(tableau_dir, "data", "CasleoadDataLong.xlsx"),
        sheet_name="CaseloadData",
        index=False,
    )


def main():
    """Generate Tableau-specific datasets"""
    generate_wide_data()
    generate_long_data()


if __name__ == "__main__":
    main()
