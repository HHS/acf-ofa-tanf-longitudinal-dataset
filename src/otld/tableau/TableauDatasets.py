import argparse
import os
import sys

import pandas as pd
from openpyxl.styles.numbers import FORMAT_NUMBER_COMMA_SEPARATED1

from otld.tableau import tableau_datasets_caseload, tableau_datasets_financial
from otld.utils import excel_to_dict, export_workbook, wide_with_index
from otld.utils.consolidation import CONSOLIDATION_INSTRUCTIONS
from otld.utils.expenditure_utils import consolidate_categories


class TableauDatasets:
    def __init__(self):
        parser = self.parse_args(sys.argv[1:])
        self._kind = parser.kind.lower()
        self._wide = parser.wide
        self._dest = parser.destination
        self._inflation = parser.inflation
        self.validate()

    def validate(self):
        if self._kind not in ["caseload", "financial"]:
            raise ValueError("Kind of data should either be caseload or financial")

        if not os.path.exists(self._wide):
            raise FileNotFoundError(f"{self._wide} does not exist.")
        elif not (self._wide.endswith(".xlsx") or self._wide.endswith(".xls")):
            raise ValueError("Long file should be an Excel workbook")

        if not os.path.exists(self._dest):
            raise FileNotFoundError(f"{self._dest} does not exist.")

        if self._kind != "financial":
            pass
        elif not self._inflation:
            raise ValueError("Must specify a file from which to draw PCE data")
        elif not os.path.exists(self._inflation):
            raise FileNotFoundError(f"{self._inflation} does not exist.")
        elif os.path.splitext(self._inflation)[-1] not in [".xls", ".xlsx", ".csv"]:
            raise ValueError("Inflation file should be either an Excel workbook or CSV")

        return self

    def parse_args(self, args: list[str]) -> argparse.Namespace:
        """Command line argument parser.

        Args:
            args (list): List of command line arguments
        """
        parser = argparse.ArgumentParser(
            prog="tanf-tableau", description="Create Tableau Datasets"
        )
        parser.add_argument("kind", type=str, help="Type of input dataset.")
        parser.add_argument("wide", type=str, help="Appended data in wide format.")
        parser.add_argument(
            "destination", type=str, help="Where to save the resultant dataset."
        )
        parser.add_argument(
            "-i",
            dest="inflation",
            type=str,
            help="Path to file to use for calculating inflation-adjusted figures",
        )

        return parser.parse_args(args)

    def generate_wide_data(self):
        frames = excel_to_dict(self._wide)

        format_options = {"skip_cols": 3}
        if self._kind == "caseload":
            format_options.update({"number_format": FORMAT_NUMBER_COMMA_SEPARATED1})

        export_workbook(
            wide_with_index(frames, f"{self._kind.title()}Data"),
            os.path.join(self._dest, f"{self._kind.title()}DataWide.xlsx"),
            format_options=format_options,
        )

    def generate_long_data(self):
        consolidation = pd.DataFrame.from_dict(CONSOLIDATION_INSTRUCTIONS)
        value_name = "Number" if self._kind == "caseload" else "Amount"
        self._frames = excel_to_dict(self._wide)
        self._df = []
        for frame in self._frames:
            df = self._frames[frame]
            if self._kind == "financial":
                consolidation.apply(lambda row: consolidate_categories(row, df), axis=1)
            df.set_index(["State", "FiscalYear"], inplace=True)
            df = df.melt(
                var_name="Category",
                value_name=value_name,
                ignore_index=False,
            )
            df["Funding"] = frame
            self._df.append(df)

        self._df = pd.concat(self._df).reset_index()

        if self._kind == "caseload":
            tableau_datasets_caseload.transform_caseload_long(self._df).to_excel(
                os.path.join(self._dest, "CaseloadDataLong.xlsx"),
                sheet_name="CaseloadData",
                index=False,
            )
        elif self._kind == "financial":
            tableau_datasets_financial.transform_financial_long(
                self._df, self._inflation
            ).to_excel(
                os.path.join(self._dest, "FinancialDataLong.xlsx"),
                sheet_name="FinancialData",
                index=False,
            )

    def generate(self):
        self.generate_wide_data()
        self.generate_long_data()


def main():
    tableau_datasets = TableauDatasets()
    tableau_datasets.generate()


if __name__ == "__main__":
    from otld import paths

    sys.argv = [
        "tanf-tableau",
        "caseload",
        os.path.join(paths.out_dir, "CaseloadDataWide.xlsx"),
        paths.scrap_dir,
        "-i",
        os.path.join(paths.inter_dir, "pce_clean.csv"),
    ]
    main()
