"""Clean PCE data"""

import os

import pandas as pd

from otld.paths import inter_dir

MONTH_MAP = {
    "01": "Jan",
    "02": "Feb",
    "03": "Mar",
    "04": "Apr",
    "05": "May",
    "06": "Jun",
    "07": "Jul",
    "08": "Aug",
    "09": "Sep",
    "10": "Oct",
    "11": "Nov",
    "12": "Dec",
}


def split_year_month(string: str) -> tuple[str]:
    """Split combined year and month.

    Args:
        string (str): Combined string containing year and month.

    Returns:
        tuple[str]: Tuple of strings containing the year and month (year, month).
    """
    year, month = string.split("M")
    year = int(year)
    month = MONTH_MAP[month]
    return year, month


def clean_pce():
    """Clean PCE data"""
    df = pd.read_excel(
        os.path.join(inter_dir, "pce.xlsx"), sheet_name="U20304-M", header=7
    )
    df = df.loc[df["Line"] == "1"]
    df.drop(df.filter(like="Unnamed").columns.tolist() + ["Line"], axis=1, inplace=True)
    df = df.melt()
    df["year"], df["month"] = zip(*df["variable"].map(split_year_month))
    df = df.pivot(index="year", columns="month", values="value")
    df.to_csv(os.path.join(inter_dir, "pce_clean.csv"))


if __name__ == "__main__":
    clean_pce()
