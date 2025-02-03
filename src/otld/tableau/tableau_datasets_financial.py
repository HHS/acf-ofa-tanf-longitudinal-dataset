"""Generate Tableau-specific long dataset"""

import os

import numpy as np
import pandas as pd

from otld.paths import inter_dir, out_dir, tableau_dir
from otld.utils import excel_to_dict, export_workbook, wide_with_index
from otld.utils.consolidation_map import CONSOLIDATION_MAP
from otld.utils.crosswalk_dict import crosswalk_dict


def calculate_pce(base_year: int) -> pd.DataFrame:
    """Output a base_pce as well as calculate pce for every federal fiscal year.

    Args:
        df (pd.DataFrame): DataFrame containing PCE information
        base_year (int): The year to which to scale inflation adjusted dollars

    Returns:
        pd.DataFrame: Data frame with pce calculated
    """
    global base_pce

    # Read in PCE
    df = pd.read_csv(os.path.join(inter_dir, "pce_clean.csv")).rename(
        columns={"year": "Year"}
    )
    df.set_index("Year", inplace=True)

    def calculate(row: pd.Series):
        try:
            index = (
                row[
                    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
                ].sum()
                + df.loc[row.name - 1, ["Oct", "Nov", "Dec"]].sum()
            ) / 12
            return index
        except KeyError:
            return np.nan

    df["pce"] = df.apply(calculate, axis=1)
    base_pce = df.loc[base_year, "pce"]

    return df.reset_index()[["Year", "pce"]]


def inflation_adjust(row: pd.Series) -> float:
    """Adjust amount for inflation

    Args:
        row (pd.Series): One expenditure entry.

    Returns:
        float: Inflation adjusted expenditure.
    """
    adjusted = row["Amount"] * base_pce / row["pce"]
    return adjusted


def update_consolidation_map(row: pd.Series, map: dict):
    instructions = row["instructions"]
    name = row["name"]
    if isinstance(instructions, int):
        map.update({str(instructions): name})
    elif isinstance(instructions, str):
        instructions = instructions.split(",")
        map.update({i.strip(): name for i in instructions})
    else:
        raise ValueError("Object is not int or str.")


def get_consolidated_column(column: str, map: dict):
    if column.find(".") == -1:
        return ""

    line = column.split(".")[0]

    try:
        return map[line]
    except KeyError:
        return ""


def generate_wide_data():
    """Generate Tableau-specific wide dataset"""
    frames = excel_to_dict(os.path.join(out_dir, "FinancialDataWide.xlsx"))
    export_workbook(
        wide_with_index(frames),
        os.path.join(tableau_dir, "data", "FinancialDataWide.xlsx"),
        format_options={"skip_cols": 3},
    )


def transform_financial_long(df: pd.DataFrame) -> pd.DataFrame:
    # Line Crosswalk
    crosswalk = pd.DataFrame.from_dict(crosswalk_dict, orient="index")
    crosswalk["Category"] = crosswalk.apply(lambda x: f"{x.name}. {x["name"]}", axis=1)
    crosswalk = crosswalk[["Category", "description"]]

    # Percentage of TANF Funds
    df = df.merge(crosswalk, how="left", on="Category")
    awarded = (
        df[
            df["Category"].map(
                lambda x: x
                in [
                    "24. Total Expenditures",
                    "2. Transfers to Child Care and Development Fund (CCDF) Discretionary",
                    "3. Transfers to Social Services Block Grant (SSBG)",
                ]
            )
        ]
        .groupby(["State", "FiscalYear", "Funding"])
        .sum(["Amount"])
        .rename(columns={"Amount": "Total"})
    )
    df = df.merge(
        awarded,
        how="left",
        on=["State", "FiscalYear", "Funding"],
    )
    df["pct_of_tanf"] = (round(df["Amount"] / df["Total"], 4) * 100).replace(
        [np.nan, np.inf, -np.inf], [0, 0, 0]
    )
    df.drop("Total", inplace=True, axis=1)

    # Percentage of total
    total = df.loc[
        df["Funding"] == "Total",
        ["State", "FiscalYear", "Category", "Amount"],
    ].rename(columns={"Amount": "Total"})
    df = df.merge(total, how="left", on=["State", "FiscalYear", "Category"])
    df["pct_of_total"] = (round(df["Amount"] / df["Total"], 4) * 100).replace(
        [np.nan, np.inf, -np.inf], [0, 0, 0]
    )
    df.drop("Total", inplace=True, axis=1)

    # Add inflation adjusted amount
    pce = calculate_pce(df["FiscalYear"].max())
    df = df.merge(pce, how="left", left_on="FiscalYear", right_on="Year")
    df["InflationAdjustedAmount"] = df.apply(inflation_adjust, axis=1)
    df.drop(["Year", "pce"], inplace=True, axis=1)

    # Add column indicating which consolidated variable is associated
    df["consolidated_column"] = df["Category"].map(
        lambda x: get_consolidated_column(x, CONSOLIDATION_MAP)
    )

    return df


def generate_long_data():
    """Generate Tableau-specific long dataset"""
    financial_data = pd.read_excel(
        os.path.join(tableau_dir, "data", "FinancialDataLongRaw.xlsx")
    )

    # Transformations
    financial_data = transform_financial_long(financial_data)

    # Export
    financial_data.to_excel(
        os.path.join(tableau_dir, "data", "FinancialDataLong.xlsx"),
        index=False,
        sheet_name="FinancialData",
    )


def main():
    generate_wide_data()
    generate_long_data()


if __name__ == "__main__":
    main()
