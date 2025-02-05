"""Class to manage appending TANF caseload and financial data"""

import os
import re
import time

import pandas as pd

from otld.utils import (
    convert_to_numeric,
    export_workbook,
    get_header,
    standardize_line_number,
    validate_data_frame,
)
from otld.utils.caseload_utils import (
    CASELOAD_FORMAT_OPTIONS,
    FAMILY_SHEET_REGEX_PATTERN,
    RECIPIENT_SHEET_REGEX_PATTERN,
    clean_dataset,
    format_final_dataset,
)
from otld.utils.crosswalk_dict import crosswalk_dict
from otld.utils.expenditure_utils import reindex_state_year


class TANFData:
    def __init__(
        self,
        type: str,
        appended_path: str,
        to_append_path: str | list[str],
        sheets: dict[list] = {},
    ):
        """Initialize TANFData class

        Args:
            type (str): Type of data being appended. Takes one of financial or caseload.
            appended_path (str): Path to the appended file. Should be xlsx format.
            to_append_path (str): Path to the file to append. Should be xlsx format.
        """
        assert appended_path.endswith(
            ".xlsx"
        ), "Appended file is not an xlsx formatted Excel Workbook"

        self._appended = pd.ExcelFile(appended_path)

        self._type = type.lower()

        self._frames = {}

        self._out_dir = os.path.split(appended_path)[0]

        year_pattern = re.compile(r"(\d{4})")

        self._to_append = {}

        # Load the data
        if isinstance(to_append_path, str):
            # Confirm file is xlsx
            assert to_append_path.endswith(
                ".xlsx"
            ), "File to append is not an xlsx formatted Excel Workbook"

            # Load file
            self._to_append["data"] = pd.ExcelFile(to_append_path)

            # Get year of file
            self._to_append["year"] = year_pattern.search(
                os.path.split(to_append_path)[1]
            ).group(0)
            self._to_append["year"] = int(self._to_append["year"])
        elif isinstance(to_append_path, list):
            # Confirm files are xlsx
            for path in to_append_path:
                assert path.endswith(
                    "xlsx"
                ), f"File to append is not an xlsx formatted Excel Workbook {path}"

            # Load files
            self._to_append["data"] = {
                self.identify_workbook_level(path): pd.ExcelFile(path)
                for path in to_append_path
            }

            # Assume year of first file is the year of all files
            self._to_append["year"] = year_pattern.search(
                os.path.split(to_append_path[0])[1]
            ).group(0)
            self._to_append["year"] = int(self._to_append["year"])
        else:
            raise TypeError(
                "Path to files to append must be a string or list of strings."
            )

        # Dictionary defining which sheets correspond to which tabs
        if sheets:
            self._sheet_dict = sheets
            self._sheet_dict.update({"internal": 0})
        else:
            self._sheet_dict = {
                "financial": {
                    "Total": "B. Total Expenditures",
                    "Federal": "C.1 Federal Expenditures",
                    "State": "C.2 State Expenditures",
                },
                "caseload": {
                    "TANF_SSP": {
                        "family": [re.compile(r"avg.*fam"), FAMILY_SHEET_REGEX_PATTERN],
                        "recipient": [
                            re.compile(r"avg.*recipient"),
                            RECIPIENT_SHEET_REGEX_PATTERN,
                        ],
                    },
                    "TANF": {
                        "family": [re.compile(r"avg.*fam"), FAMILY_SHEET_REGEX_PATTERN],
                        "recipient": [
                            re.compile(r"avg.*recipient"),
                            RECIPIENT_SHEET_REGEX_PATTERN,
                        ],
                    },
                    "SSP_MOE": {
                        "family": [re.compile(r"avg.*fam"), FAMILY_SHEET_REGEX_PATTERN],
                        "recipient": [
                            re.compile(r"avg.*recipient"),
                            RECIPIENT_SHEET_REGEX_PATTERN,
                        ],
                    },
                },
            }
            self._sheet_dict.update({"internal": 1})

    @property
    def appended(self):
        """Base file containing appended data"""
        return self._appended

    @property
    def to_append(self):
        """File, or list of files, to append to base file"""
        return self._to_append

    @property
    def type(self):
        """The kind of data being appended"""
        return self._type

    @property
    def sheet_dict(self):
        """Dictionary of sheets from which to extract information"""
        return self._sheet_dict

    def identify_workbook_level(self, path: str):
        """Identify the level of the caseload workbook"""
        if self._type == "caseload":
            if re.search(r"tanf?_caseload", path):
                return "TANF"
            elif re.search(r"tanf?ssp_caseload", path):
                return "TANF_SSP"
            elif re.search(r"(?<!tan)(?<!tanf)ssp_caseload", path):
                return "SSP_MOE"
            else:
                raise ValueError(f"Cannot process workbook: {path}")

    def get_current_sheet(self):
        """Return the current sheet"""
        return self._sheet_dict[self._type][self._level]

    def get_worksheets(self):
        """Get worksheets that correspond to the current level"""
        if self._type == "financial":
            self._sheets = self.get_current_sheet()
            return self
        elif self._type == "caseload":
            if not self._sheet_dict["internal"]:
                self._sheets = list(self.get_current_sheet().values())
                return self
            sheets = []
            sheet_names = self._to_append["data"][self._level].sheet_names
            level_patterns = self.get_current_sheet()
            for patterns in level_patterns.values():
                if not isinstance(patterns, list):
                    patterns = [patterns]

                found = False

                for pattern in patterns:
                    for sheet in sheet_names:
                        clean_sheet = re.sub(r"\W", "", sheet).lower().strip()
                        if pattern.search(clean_sheet):
                            sheets.append(sheet)
                            found = True
                            break
                        if found:
                            break
                    if found:
                        break

                if not found:
                    raise ValueError(f"No matching sheets found: {self._level}")

            self._sheets = sheets
            return self

    def append(self):
        """Append financial or caseload data"""

        # Append data
        for level in self._sheet_dict[self._type]:
            self._level = level
            self.get_worksheets()
            self.get_df()
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

    def get_header_wrapper(self, df: pd.DataFrame) -> pd.DataFrame:
        """Wrapper for get_header

        Re-runs with the concatenate option if the header has duplicates, numeric columns
        or the data frame is empty

        Args:
            df (pd.DataFrame): DataFrame to search in for a header.

        Returns:
            pd.DataFrame: DataFrame columns renamed and any leading columns dropped.
        """
        new_df = get_header(df)

        if (
            new_df.empty
            or any([isinstance(col, (int, float)) for col in new_df.columns])
            or new_df.columns.duplicated().any()
        ):
            new_df = get_header(df, concatenate=True)

        return new_df

    def get_df(self):
        """Get data from file to append

        Args:
            level (str): The current funding level.
            worksheet (str): The worksheet to extract data from.
        """
        worksheet = self._sheets
        level = self._level
        if self._type == "financial":
            df = pd.read_excel(
                self._to_append["data"], sheet_name=worksheet, header=None
            )
            df = self.get_header_wrapper(df)
            df.columns = [col.strip() for col in df.columns]

            # Add year column
            df["Year"] = self._to_append["year"]

            # Drop if state is missing
            state_column = df.filter(regex=re.compile("^state$", re.IGNORECASE)).columns
            state_column = state_column[0]
            df.dropna(subset=[state_column], inplace=True)
            df[state_column] = df[state_column].map(lambda x: x.strip())
            df.set_index([state_column, "Year"], inplace=True)
            df.index.rename(["State", "FiscalYear"], inplace=True)

            # Convert to numeric
            df = df.apply(convert_to_numeric)
            df.fillna(0, inplace=True)

            self._df = df
            self.rename_columns()
            self.validate_data_frame()

        elif self._type == "caseload":
            data = []
            for sheet in worksheet:
                df = pd.read_excel(
                    self._to_append["data"][level], sheet_name=sheet, header=None
                )
                df = self.get_header_wrapper(df)
                df = clean_dataset(df)
                data.append(df)

            df = data[0].merge(data[1], on="State", how="outer", indicator=True)
            assert (df["_merge"] == "both").all(), "Imperfect merge."
            df.drop("_merge", axis=1, inplace=True)

            self._df = df
            self.rename_columns()

            self._df["FiscalYear"] = self._to_append["year"]
            self._df = format_final_dataset(self._df)
            self._df.set_index(["State", "FiscalYear"], inplace=True)
            self._df = reindex_state_year(self._df, ["State", "FiscalYear"])
            self.validate_data_frame()

        # Currently caseload data fails the numeric check because "-" and other string
        # characters are allowed in columns
        # self.validate_data_frame()

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
            # Drop if column is unnamed
            df.drop(df.filter(regex="^Unnamed: \\d+$|^$").columns, axis=1, inplace=True)
        # Handle renaming in the case of caseload data
        elif self._type == "caseload":

            def rename(column: str):
                family_column = re.search(r"^\s*(one|two|no)", column, re.IGNORECASE)
                recipient_column = re.search(
                    r"^\s*(adult|children)", column, re.IGNORECASE
                )
                misc_column = re.search(r"^\s*(total|state)", column, re.IGNORECASE)
                if family_column:
                    column = f"{family_column.group(1)} Parent Families".title()
                elif recipient_column:
                    column = f"{recipient_column.group(1)} Recipients".title()
                elif misc_column:
                    column
                else:
                    raise ValueError(
                        "Column does not match expected patterns for family or recipient sheets"
                    )

                return column

            self._df.columns = self._df.columns.map(rename)

    def validate_data_frame(self):
        """Wraps validate_data_frame; Ensures a copy is used"""

        df = self._df.copy()
        validate_data_frame(df)

    def export_workbook(self):
        """Export data to Excel workbook"""

        if self._type == "caseload":
            format_options = CASELOAD_FORMAT_OPTIONS
        else:
            format_options = {}

        title = f"{self._type.title()}Data"
        # Export wide data
        current_date = time.strftime("%Y%m%d", time.gmtime())
        path = os.path.join(
            self._out_dir,
            f"{title}Wide_{current_date}.xlsx",
        )
        export_workbook(self._frames, path, format_options=format_options)

        # Reshape and export long data
        path = os.path.join(
            self._out_dir,
            f"{title}Long_{current_date}.xlsx",
        )

        self._frames[title] = []
        for frame in self._frames:
            if frame == title:
                continue
            self._frames[frame] = self._frames[frame].melt(
                var_name="Category", value_name="Amount", ignore_index=False
            )
            self._frames[frame]["Funding"] = frame
            self._frames[title].append(self._frames[frame])

        self._frames[title] = pd.concat(self._frames[title])
        for frame in list(self._frames.keys()):
            if frame != title:
                del self._frames[frame]

        export_workbook(self._frames, path, format_options=format_options)

    def close_excel_files(self):
        """Close all files"""
        workbooks = self._to_append["data"]
        if isinstance(workbooks, dict):
            for book in workbooks.values():
                book.close()
        else:
            workbooks.close()

        self.appended.close()


if __name__ == "__main__":
    # from otld.paths import test_dir

    # tanf_data = TANFData(
    #     "financial",
    #     os.path.join(test_dir, "FinancialDataWide.xlsx"),
    #     os.path.join(test_dir, "mock", "tanf_financial_data_fy_2024.xlsx"),
    # )

    from otld.paths import test_dir

    tanf_data = TANFData(
        "caseload",
        os.path.join(test_dir, "CaseloadDataWide.xlsx"),
        [
            os.path.join(test_dir, "mock", "fy2024_ssp_caseload.xlsx"),
            os.path.join(test_dir, "mock", "fy2024_tanf_caseload.xlsx"),
            os.path.join(test_dir, "mock", "fy2024_tanfssp_caseload.xlsx"),
        ],
        {
            "caseload": {
                "TANF": {
                    "family": "fycy2024-families",
                    "recipient": "fycy2024-recipients",
                },
                "SSP_MOE": {
                    "family": "Avg Month Num Fam",
                    "recipient": "Avg Mo. Num Recipient",
                },
                "TANF_SSP": {
                    "family": "fycy2024-families",
                    "recipient": "Avg Mo. Num Recipient",
                },
            }
        },
    )

    tanf_data.append()
