"""Class to manage appending TANF caseload and financial data"""

import os
import re
import time

import openpyxl
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet

from otld.format_appended_files import export_workbook
from otld.utils import (
    convert_to_numeric,
    delete_empty_columns,
    get_column_names,
    standardize_line_number,
)
from otld.utils.crosswalk_2014_2015 import crosswalk_dict


class TANFData:
    def __init__(self, type: str, appended_path: str, to_append_path: str):
        """Initialize TANFData class

        Args:
            type (str): Type of data being appended. Takes one of financial or caseload.
            appended_path (str): Path to the appended file. Should be xlsx format.
            to_append_path (str): Path to the file to append. Should be xlsx format.
        """
        assert appended_path.endswith(
            ".xlsx"
        ), "Appended file is not an xlsx formatted Excel Workbook"
        assert to_append_path.endswith(
            ".xlsx"
        ), "File to append is not an xlsx formatted Excel Workbook"

        self._appended = pd.ExcelFile(appended_path)

        self._to_append = {}
        self._to_append["data"] = openpyxl.load_workbook(to_append_path, data_only=True)
        self._to_append["year"] = re.search(
            r"(\d{4})", os.path.split(to_append_path)[1]
        ).group(0)
        self._to_append["year"] = int(self._to_append["year"])

        self._type = type.lower()

        self._frames = {}

        self._out_dir = os.path.split(appended_path)[0]

    @property
    def appended(self):
        return self._appended

    @property
    def to_append(self):
        return self._to_append

    @property
    def type(self):
        return self._type

    def append(self):
        """Append financial or caseload data"""

        # Dictionary defining which sheets correspond to which tabs
        sheet_dict = {
            "financial": {
                "Total": "B. Total Expenditures",
                "Federal": "C.1 Federal Expenditures",
                "State": "C.2 State Expenditures",
            },
            "caseload": {},
        }

        # Append data
        for level in sheet_dict[self._type]:
            sheet = sheet_dict[self._type][level]
            self.get_df(self._to_append["data"][sheet])
            self._frames[level] = pd.concat(
                [
                    pd.read_excel(
                        self._appended,
                        sheet_name=level,
                        index_col=[0, 1],
                    ),
                    self._df,
                ]
            )
            del self._df
        self.export_workbook()

    def get_df(self, worksheet: Worksheet):
        """Get data from file to append

        Args:
            worksheet (Worksheet): The worksheet to extract data from.
        """
        if self._type == "financial":
            delete_empty_columns(worksheet)
            columns, i = get_column_names(worksheet)
            data = list(worksheet.values)[i:]

            df = pd.DataFrame(data, columns=columns)

            # Add year column
            df["Year"] = self._to_append["year"]

            # Drop if state is missing
            df.dropna(subset=["STATE"], inplace=True)
            df["STATE"] = df["STATE"].map(lambda x: x.strip())
            df.set_index(["STATE", "Year"], inplace=True)
            df.index.rename(["State", "Year"], inplace=True)

            # Convert to numeric
            df = df.apply(convert_to_numeric)
            df.fillna(0, inplace=True)

            self._df = df
            self.rename_columns()

    def rename_columns(self):
        """Rename the columns in TANFData._df"""

        df = self._df

        # Handle renaming in the case of financial data
        if self._type == "financial":
            columns = df.columns.tolist()
            numbers = [re.match(r"(\d[\w\.]+?)\s", column) for column in columns]

            assert all(numbers), "Not all columns contain line number"

            numbers = [match.group(1).replace(".", "") for match in numbers]
            numbers = [standardize_line_number(number) for number in numbers]

            # Convert line numbers to column names using crosswalk_dict
            renamer = {
                columns[i]: crosswalk_dict[number]["name"]
                for i, number in enumerate(numbers)
            }

            df.rename(columns=renamer, inplace=True)
        # Handle renaming in the case of caseload data
        elif self._type == "caseload":
            pass

    def export_workbook(self):
        """Export data to Excel workbook"""

        # Export wide data
        path = os.path.join(
            self._out_dir,
            f"FinancialDataWide_{time.strftime("%Y%m%d", time.gmtime())}.xlsx",
        )
        export_workbook(self._frames, path)

        # Reshape and export long data
        path = path = os.path.join(
            self._out_dir,
            f"FinancialDataLong_{time.strftime("%Y%m%d", time.gmtime())}.xlsx",
        )

        self._frames["FinancialData"] = []
        for frame in self._frames:
            if frame == "FinancialData":
                continue
        self._frames[frame] = self._frames[frame].melt(
            var_name="Category", value_name="Amount", ignore_index=False
        )
        self._frames[frame]["Level"] = frame
        self._frames["FinancialData"].append(self._frames[frame])

        self._frames["FinancialData"] = pd.concat(self._frames["FinancialData"])
        for frame in list(self._frames.keys()):
            if frame != "FinancialData":
                del self._frames[frame]

        export_workbook(self._frames, path)


if __name__ == "__main__":
    from otld.paths import scrap_dir

    tanf_data = TANFData(
        "financial",
        os.path.join(scrap_dir, "FinancialDataWide.xlsx"),
        os.path.join(scrap_dir, "tanf_financial_data_fy_2024.xlsx"),
    )

    tanf_data.append()
