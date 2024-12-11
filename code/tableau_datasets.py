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
    financial_data.to_excel(
        os.path.join(tableau_dir, "data", "FinancialDataLong.xlsx"),
        index=False,
        sheet_name="FinancialData",
    )


if __name__ == "__main__":
    main()
