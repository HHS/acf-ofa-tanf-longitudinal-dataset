"""Class for validation checks of caseload and financial data"""

import os
import re

import pandas as pd

from otld.utils.crosswalk_2014_2015 import crosswalk_dict, map_columns
from otld.utils.openpyxl_utils import export_workbook


class GenericChecker:
    def __init__(self, df: pd.DataFrame, level: str, kind: str, action: str = "error"):
        """Initialize instance of GenericChecker class

        Args:
            df (pd.DataFrame): TANF data DataFrame
            level (str): Funding level
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

    @property
    def df(self):
        """Financial data frame"""
        return self._df

    @property
    def level(self):
        """Funding level (State, Federal, Total)"""
        return self._level

    @property
    def action(self):
        """Action to be taken when an assertion fails"""
        return self._action

    @property
    def kind(self):
        """ACF Instructions (196, 196R, Appended)"""
        return self._kind

    def export(self, path: str | os.PathLike, sheet_name: str = None, **kwargs) -> None:
        """Export checks to a workbook

        Args:
            path (str | os.PathLike): Path to export checks to.
            sheet_name (str, optional): An optional sheet name for the checks. Defaults to None.
        """
        export_workbook(self._checks, path, **kwargs)


class FinancialDataChecker(GenericChecker):
    """Implement validation checks for the financial data"""

    def __init__(self, df: pd.DataFrame, level: str, kind: str, action: str = "error"):
        """Initialize FinancialDataChecker

        Args:
            df (pd.DataFrame): Financial data DataFrame
            level (str): Funding level (Federal, State, Total)
            kind (str): ACF Instructions (196, 196R, Appended)
            action (str, optional): Action to take when an assertion fails.
            Defaults to "error", but also accepts "export"
        """
        super().__init__(df, level, kind, action)
        self.names_to_lines()

    def names_to_lines(self):
        """Rename columns to 196R line numbers"""
        if self._kind == "196":
            self._df = map_columns(self._df, crosswalk_dict)
        elif self._kind == "196R":
            pass
        else:
            self._df.columns = self._df.columns.map(
                lambda x: re.match(r"\w+", x).group(0)
            )

    def lines_to_names(self, df: pd.DataFrame):
        """Rename line numbers to human readable names"""

        def get_name(line: str):
            entry = crosswalk_dict.get(line)
            return entry["name"] if entry else line

        return df.columns.map(get_name)

    def check(self):
        """Choose which check(s) to perform"""
        if self._level == "Federal":
            self.federal_financial_data_checks()
        elif self._level == "State":
            pass
        elif self._level == "Total":
            pass

    def federal_financial_data_checks(self):
        """Execute federal financial data checks"""
        checks = self._checks
        df = self._df.copy()
        df["funds"] = df["1"] + df["5"] - df["2"] - df["3"] - df["24"]
        df["obligations"] = df["27"] + df["28"]
        funds_check = df["funds"] == df["obligations"]
        try:
            assert (
                funds_check.all()
            ), "awarded + carryover - transfers - expenditures != unliquidated + unobligated"
        except AssertionError as e:
            if self._action == "error":
                raise e

            failed = df[~funds_check]
            failed.columns = self.lines_to_names(failed)
            checks["funds_obligations"] = failed

        # Check that sum of expenditure columns equals total expenditures
        df = self._df.copy()
        non_expenditure_cols = df.filter(
            regex=r"^1$|^2$|^3$|^4$|^5$|\d+[abc]|24|27|28"
        ).columns.tolist()
        expenditure_cols = df.columns.difference(non_expenditure_cols).tolist()
        if self._kind == "196":
            expenditure_cols.extend(["11a", "22a", "22c"])
        df["expenditures"] = df[expenditure_cols].sum(axis=1)
        expenditure_cols = expenditure_cols + ["expenditures", "24"]

        expenditure_check = df["expenditures"] == df["24"]
        try:
            assert (
                expenditure_check.all()
            ), "Sum of expenditures does not equal total expenditure column"
        except AssertionError as e:
            if self._action == "error":
                raise e

            failed = df[~expenditure_check][expenditure_cols]
            failed.columns = self.lines_to_names(failed)
            failed["difference"] = df["24"] - df["expenditures"]
            checks["expenditures"] = failed


class CaseloadDataChecker(GenericChecker):
    def __init__(
        self,
        df: pd.DataFrame | dict[pd.DataFrame],
        level: str = "",
        action: str = "error",
    ):
        """Initialize CaseloadDataChecker

        Args:
            df (pd.DataFrame): Caseload data DataFrame
            level (str): Funding level (TANF, TANF-SSP, SSP-MOE)
            action (str, optional): Action to take when an assertion fails. Defaults to "error".
        """
        super().__init__(df, level, None, action)

    def check(self):
        """Run caseload data checks"""
        # If a dictionary of data frames, then loop through
        if isinstance(self._df, dict):
            self._df_dict = self._df
            for frame in self._df_dict:
                self._level = frame
                self._df = self._df_dict[frame]
                self.caseload_data_checks()
        # Otherwise, run checks directly
        else:
            self.caseload_data_checks()

        return self

    def caseload_data_checks(self):
        """Generic caseload data checks"""
        checks = self._checks
        df = self._df.copy()

        # Check that the sum of families vars equals the total
        df["families_dif"] = df["Total Families"] - df[
            ["Two Parent Families", "One Parent Families", "No Parent Families"]
        ].sum(axis=1)

        try:
            family_dif = df["families_dif"].map(lambda x: x >= -2 and x <= 2)
            assert family_dif.all(), "Some differences in families"
        except AssertionError as e:
            if self._action == "error":
                raise e

            failed = df[~family_dif].filter(regex="(F|f)amilies")
            checks[f"family_sum{self._level}"] = failed

        # Check that the sum of recipients vars equals the total
        df["recipients_dif"] = df["Total Recipients"] - df[
            ["Adult Recipients", "Children Recipients"]
        ].sum(axis=1)

        try:
            recipient_dif = df["recipients_dif"].map(lambda x: x >= -2 and x <= 2)
            assert recipient_dif.all(), "Some differences in recipients"
        except AssertionError as e:
            if self._action == "error":
                raise e

            failed = df[~recipient_dif].filter(regex="(R|r)ecipients")
            checks[f"recipient_sum{self._level}"] = failed
