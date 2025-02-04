import argparse
import os
import sys

import pandas as pd
from openpyxl.styles.numbers import FORMAT_NUMBER_COMMA_SEPARATED1

from otld.tableau import tableau_datasets_caseload, tableau_datasets_financial
from otld.utils import excel_to_dict, export_workbook, wide_with_index


class TableauDatasets:
    def __init__(self):
        parser = self.parse_args(sys.argv[1:])
        self._kind = parser.kind.lower()
        self._wide = parser.wide
        self._long = parser.long
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

        if not os.path.exists(self._long):
            raise FileNotFoundError(f"{self._long} does not exist.")
        elif not (self._long.endswith(".xlsx") or self._long.endswith(".xls")):
            raise ValueError("Long file should be an Excel workbook")

        if not os.path.exists(self._dest):
            raise FileNotFoundError(f"{self._dest} does not exist.")

        if not self._inflation:
            return self

        if not os.path.exists(self._inflation):
            raise FileNotFoundError(f"{self._inflation} does not exist.")
        elif os.path.splitext(self._inflation)[-1] not in [".xls", ".xlsx", ".csv"]:
            raise ValueError("Inflation file should be either an Excel workbook or CSV")

    def parse_args(self, args: list[str]) -> argparse.Namespace:
        """Command line argument parser.

        Args:
            args (list): List of command line arguments
        """
        parser = argparse.ArgumentParser(
            prog="tanf-tableau", description="Create Tableau Datasets"
        )
        parser.add_argument("kind", type=str, help="Type of data to append.")
        parser.add_argument("wide", type=str, help="Appended data in wide format.")
        parser.add_argument("long", type=str, help="Appended data in long format.")
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
        self._df = pd.read_excel(self._long)
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
