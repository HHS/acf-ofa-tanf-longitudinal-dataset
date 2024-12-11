import os

import pandas as pd

from otld.paths import input_dir, out_dir, tableau_dir


def main():
    financial_data = pd.read_excel(os.path.join(out_dir, "FinancialDataLong.xlsx"))
    crosswalk = pd.read_excel(
        os.path.join(input_dir, "Instruction Crosswalk.xlsx"), sheet_name="crosswalk"
    )

    crosswalk["Category"] = crosswalk.apply(
        lambda x: f"{x["196R"]}. {x["name"]}", axis=1
    )
    crosswalk = crosswalk[["Category", "description"]]

    financial_data = financial_data.merge(crosswalk, how="left", on="Category")
    awarded = financial_data[financial_data["Category"] == "1. Awarded"].rename(
        columns={"Amount": "Total"}
    )
    financial_data = financial_data.merge(
        awarded[["State", "Year", "Level", "Total"]],
        how="left",
        on=["State", "Year", "Level"],
    )
    financial_data["pct_of_total"] = (
        round(financial_data["Amount"] / financial_data["Total"], 4) * 100
    )
    financial_data.loc[financial_data["Category"] == "1. Awarded", "pct_of_total"] = (
        None
    )
    financial_data.drop("Total", inplace=True, axis=1)

    financial_data.to_excel(
        os.path.join(tableau_dir, "data", "FinancialDataLong.xlsx"),
        index=False,
        sheet_name="FinancialData",
    )


if __name__ == "__main__":
    main()
