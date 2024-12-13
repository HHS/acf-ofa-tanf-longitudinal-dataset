import os

import numpy as np
import pandas as pd

from otld.paths import input_dir, tableau_dir


def main():
    financial_data = pd.read_excel(
        os.path.join(tableau_dir, "data", "FinancialDataLongRaw.xlsx")
    )
    crosswalk = pd.read_excel(
        os.path.join(input_dir, "Instruction Crosswalk.xlsx"), sheet_name="crosswalk"
    )

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
        .groupby(["State", "Year", "Level"])
        .sum(["Amount"])
        .rename(columns={"Amount": "Total"})
    )
    financial_data = financial_data.merge(
        awarded,
        how="left",
        on=["State", "Year", "Level"],
    )
    financial_data["pct_of_tanf"] = (
        round(financial_data["Amount"] / financial_data["Total"], 4) * 100
    ).replace([np.nan, np.inf, -np.inf], [0, 0, 0])
    financial_data.drop("Total", inplace=True, axis=1)

    # Percentage of total
    total = financial_data.loc[
        financial_data["Level"] == "Total",
        ["State", "Year", "Category", "Amount"],
    ].rename(columns={"Amount": "Total"})
    financial_data = financial_data.merge(
        total, how="left", on=["State", "Year", "Category"]
    )
    financial_data["pct_of_total"] = (
        round(financial_data["Amount"] / financial_data["Total"], 4) * 100
    ).replace([np.nan, np.inf, -np.inf], [0, 0, 0])
    financial_data.drop("Total", inplace=True, axis=1)

    # Export
    financial_data.to_excel(
        os.path.join(tableau_dir, "data", "FinancialDataLong.xlsx"),
        index=False,
        sheet_name="FinancialData",
    )


if __name__ == "__main__":
    main()
