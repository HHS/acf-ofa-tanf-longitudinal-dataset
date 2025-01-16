"""Generate Tableau-specific long dataset"""

import os

import numpy as np
import pandas as pd

from otld.paths import input_dir, inter_dir, out_dir, tableau_dir
from otld.utils import excel_to_dict, export_workbook
from otld.utils.expenditure_utils import reindex_state_year


def load_cpi_u() -> pd.DataFrame:
    """Load the urban Consumer price index (CPI) data

    Returns:
        pd.DataFrame: CPI-U data frame
    """
    cpi = pd.read_excel(os.path.join(inter_dir, "cpi_u.xlsx"))
    skip = 0
    for i in range(cpi.shape[0]):
        if cpi.iloc[i, 0] == "Year":
            skip = i
            break

    cpi = pd.read_excel(os.path.join(inter_dir, "cpi_u.xlsx"), header=skip + 1)

    return cpi


def calculate_cpi(cpi: pd.DataFrame, base_year: int) -> pd.DataFrame:
    """Output a base_cpi as well as calculate cpi for every federal fiscal year.

    Args:
        cpi (pd.DataFrame): CPI data frame
        base_year (int): The year to which to scale inflation adjusted dollars

    Returns:
        pd.DataFrame: Data frame with cpi calculated
    """
    global base_cpi
    cpi.set_index("Year", inplace=True)

    def calculate(row: pd.Series):
        try:
            index = (
                row[
                    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
                ].sum()
                + cpi.loc[row.name - 1, ["Oct", "Nov", "Dec"]].sum()
            ) / 12
            return index
        except KeyError:
            return np.nan

    cpi["cpi"] = cpi.apply(calculate, axis=1)
    base_cpi = cpi.loc[base_year, "cpi"]

    return cpi.reset_index()[["Year", "cpi"]]


def inflation_adjust(row: pd.Series) -> float:
    """Adjust amount for inflation

    Args:
        row (pd.Series): One expenditure entry.

    Returns:
        float: Inflation adjusted expenditure.
    """
    adjusted = row["Amount"] * base_cpi / row["cpi"]
    return adjusted


def wide_with_index(frames: dict[pd.DataFrame]):
    out = pd.DataFrame()
    for name, data in frames.items():
        data = data.copy()
        data.insert(0, "Funding", name)

        if out.empty:
            out = data
        else:
            out = pd.concat([out, data])

    out.set_index(["Funding", "FiscalYear", "State"], inplace=True)
    out.sort_index(
        level=["Funding", "FiscalYear", "State"],
        ascending=[False, False, True],
        inplace=True,
    )
    out = reindex_state_year(out, list(out.index.names))

    return {"FinancialData": out.reset_index()}


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
    cpi_u = load_cpi_u()
    cpi_u = calculate_cpi(cpi_u, financial_data["FiscalYear"].max())
    financial_data = financial_data.merge(
        cpi_u, how="left", left_on="FiscalYear", right_on="Year"
    )
    financial_data["InflationAdjustedAmount"] = financial_data.apply(
        inflation_adjust, axis=1
    )
    financial_data.drop(["Year", "cpi"], inplace=True, axis=1)

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
