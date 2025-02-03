"""Generate Tableau-specific long dataset"""

import os

import numpy as np
import pandas as pd

from otld.paths import input_dir, inter_dir, out_dir, tableau_dir
from otld.utils import excel_to_dict, export_workbook, wide_with_index


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


def generate_long_data():
    """Generate Tableau-specific long dataset"""
    instructions = pd.ExcelFile(os.path.join(input_dir, "Instruction Crosswalk.xlsx"))
    financial_data = pd.read_excel(
        os.path.join(tableau_dir, "data", "FinancialDataLongRaw.xlsx")
    )
    crosswalk = pd.read_excel(instructions, sheet_name="crosswalk")

    crosswalk["Category"] = crosswalk.apply(
        lambda x: f"{x["196R"]}. {x["name"]}", axis=1
    )
    crosswalk = crosswalk[["Category", "description"]]

    # Percentage of TANF Funds
    financial_data = financial_data.merge(crosswalk, how="left", on="Category")
    awarded = (
        financial_data[
            financial_data["Category"].map(
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
    financial_data = financial_data.merge(
        awarded,
        how="left",
        on=["State", "FiscalYear", "Funding"],
    )
    financial_data["pct_of_tanf"] = (
        round(financial_data["Amount"] / financial_data["Total"], 4) * 100
    ).replace([np.nan, np.inf, -np.inf], [0, 0, 0])
    financial_data.drop("Total", inplace=True, axis=1)

    # Percentage of total
    total = financial_data.loc[
        financial_data["Funding"] == "Total",
        ["State", "FiscalYear", "Category", "Amount"],
    ].rename(columns={"Amount": "Total"})
    financial_data = financial_data.merge(
        total, how="left", on=["State", "FiscalYear", "Category"]
    )
    financial_data["pct_of_total"] = (
        round(financial_data["Amount"] / financial_data["Total"], 4) * 100
    ).replace([np.nan, np.inf, -np.inf], [0, 0, 0])
    financial_data.drop("Total", inplace=True, axis=1)

    # Add inflation adjusted amount
    pce = calculate_pce(financial_data["FiscalYear"].max())
    financial_data = financial_data.merge(
        pce, how="left", left_on="FiscalYear", right_on="Year"
    )
    financial_data["InflationAdjustedAmount"] = financial_data.apply(
        inflation_adjust, axis=1
    )
    financial_data.drop(["Year", "pce"], inplace=True, axis=1)

    # Add column indicating which consolidated variable is associated
    consolidations = pd.read_excel(instructions, sheet_name="consolidated_categories")
    consolidation_map = {}
    consolidations.apply(
        lambda row: update_consolidation_map(row, consolidation_map), axis=1
    )
    financial_data["consolidated_column"] = financial_data["Category"].map(
        lambda x: get_consolidated_column(x, consolidation_map)
    )

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
