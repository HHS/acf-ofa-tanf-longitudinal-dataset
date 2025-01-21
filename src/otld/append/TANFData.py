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
    FAMILY_SHEET_REGEX_PATTERN,
    RECIPIENT_SHEET_REGEX_PATTERN,
    clean_dataset,
    format_final_dataset,
)
from otld.utils.crosswalk_2014_2015 import crosswalk_dict


class TANFData:
    def __init__(self, type: str, appended_path: str, to_append_path: str | list[str]):
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

    @property
    def appended(self):
        return self._appended

    @property
    def to_append(self):
        return self._to_append

    @property
    def type(self):
        return self._type

    @property
    def sheet_dict(self):
        return self._sheet_dict

    def identify_workbook_level(self, path: str):
        if self._type == "caseload":
            if re.search(r"tanf?_caseload", path):
                return "TANF"
            elif re.search(r"tanf?ssp_caseload", path):
                return "TANF_SSP"
            elif re.search(r"(?<!tan)(?<!tanf)ssp_caseload", path):
                return "SSP_MOE"
            else:
                raise ValueError(f"Cannot process workbook: {path}")

    def get_worksheets(self, level: str):
        if self._type == "financial":
            sheet = self._sheet_dict[self._type][level]
            return sheet
        elif self._type == "caseload":
            sheets = []
            sheet_names = self._to_append["data"][level].sheet_names
            level_patterns = self._sheet_dict[self._type][level]
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
                    raise ValueError(f"No matching sheets found: {level}")

            return sheets

    def append(self):
        """Append financial or caseload data"""

        # Append data
        for level in self._sheet_dict[self._type]:
            sheet = self.get_worksheets(level)
            self.get_df(level, sheet)
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

    def get_df(self, level: str, worksheet: str | list[str]):
        """Get data from file to append

        Args:
            level (str): The current funding level.
            worksheet (str): The worksheet to extract data from.
        """
        if self._type == "financial":
            df = pd.read_excel(
                self._to_append["data"], sheet_name=worksheet, header=None
            )
            df = get_header(df)
            df.columns = [col.strip() for col in df.columns]

            # Add year column
            df["Year"] = self._to_append["year"]

            # Drop if state is missing
            df.dropna(subset=["STATE"], inplace=True)
            df["STATE"] = df["STATE"].map(lambda x: x.strip())
            df.set_index(["STATE", "Year"], inplace=True)
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
                df = get_header(df)
                df = clean_dataset(df)
                data.append(df)

            df = data[0].merge(data[1], on="State", how="outer", indicator=True)
            assert (df["_merge"] == "both").all(), "Imperfect merge."
            df.drop("_merge", axis=1, inplace=True)

            df["FiscalYear"] = self._to_append["year"]
            df = format_final_dataset(df)
            df.set_index(["State", "FiscalYear"], inplace=True)

            self._df = df
            # self.validate_data_frame()

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
        # Handle renaming in the case of caseload data
        elif self._type == "caseload":
            pass

    def validate_data_frame(self):
        df = self._df.copy()
        validate_data_frame(df)

    def export_workbook(self):
        """Export data to Excel workbook"""

        title = f"{self._type.title()}Data"
        # Export wide data
        current_date = time.strftime("%Y%m%d", time.gmtime())
        path = os.path.join(
            self._out_dir,
            f"{title}Wide_{current_date}.xlsx",
        )
        export_workbook(self._frames, path)

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

        export_workbook(self._frames, path)


if __name__ == "__main__":
    from otld.paths import scrap_dir

    # tanf_data = TANFData(
    #     "financial",
    #     os.path.join(scrap_dir, "FinancialDataWide.xlsx"),
    #     os.path.join(scrap_dir, "tanf_financial_data_fy_2024.xlsx"),
    # )

    tanf_data = TANFData(
        "caseload",
        os.path.join(scrap_dir, "CaseloadDataWide.xlsx"),
        [
            os.path.join(scrap_dir, "fy2024_ssp_caseload.xlsx"),
            os.path.join(scrap_dir, "fy2024_tanf_caseload.xlsx"),
            os.path.join(scrap_dir, "fy2024_tanssp_caseload.xlsx"),
        ],
    )

    tanf_data.append()
