"""Class for validation checks of expenditure data"""

import os
import re

import pandas as pd

from otld.utils.crosswalk_2014_2015 import crosswalk_dict, map_columns


class ExpenditureDataChecker:
    """Implement validation checks for the expenditure data"""

    def __init__(self, df: pd.DataFrame, level: str, kind: str, action: str = "error"):
        """Initialize instance of ExpenditureDataChecker class

        Args:
            df (pd.DataFrame): Expenditure data DataFrame
            level (str): Funding level (Federal, State, Total)
            kind (str): ACF Instructions (196, 196R, Appended)
            action (str, optional): Action to take when an assertion fails.
            Defaults to "error", but also accepts "export"
        """
        self._df = df.copy()
        self._level = level
        self._action = action
        if action != "error":
            self._checks = {}

        self._kind = kind
        self.rename_columns()

    @property
    def df(self):
        return self._df

    @property
    def level(self):
        return self._level

    @property
    def action(self):
        return self._action

    @property
    def kind(self):
        return self._kind

    def rename_columns(self):
        """Rename columns to 196R line numbers"""
        if self._kind == "196":
            self._df = map_columns(self._df, crosswalk_dict)
        elif self._kind == "196R":
            pass
        else:
            self._df.columns = self._df.columns.map(
                lambda x: re.match(r"\w+", x).group(0)
            )

    def check(self):
        """Choose which check(s) to perform"""
        if self._level == "Federal":
            self.federal_expenditure_data_checks()
        elif self._level == "State":
            pass
        elif self._level == "Total":
            pass

    def federal_expenditure_data_checks(self):
        """Execute federal expenditure data checks"""
        checks = self._checks
        df = self._df
        df["funds"] = df["1"] + df["5"] - df["2"] - df["3"] - df["24"]
        df["obligations"] = df["27"] + df["28"]
        funds_check = df["funds"] == df["obligations"]
        try:
            assert (
                funds_check.all()
            ), "awarded + carryover - transfers - expenditures != unliquidated + unobligated"
        except AssertionError as e:
            if self._action == "error":
                raise (e)

            failed = df[~funds_check]
            checks["funds_obligations"] = failed

    def export(self, path: str | os.PathLike, sheet_name: str = None) -> None:
        """Export data in checks dictionary to an Excel workbook

        Args:
            path (str | os.PathLike): The workbook to export to
            sheet_name (str, optional): A sheet to export to. This argument can only be
            provided if only a single check is being conducted. Defaults to None.
        """
        if sheet_name is not None:
            assert len(self._checks.values()) == 1
        writer = pd.ExcelWriter(path)
        for check, result in self._checks.items():
            result.to_excel(writer, sheet_name=sheet_name or check)

        writer.close()
