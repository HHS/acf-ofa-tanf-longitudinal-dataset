"""Utilities to support caseload.py"""

import re
import traceback
from typing import List, Optional

import numpy as np
import pandas as pd
from openpyxl.styles.numbers import BUILTIN_FORMATS

from otld.utils import get_header, long_notes

OUTPUT_COLUMNS = [
    "FiscalYear",
    "State",
    "Total Families",
    "Two Parent Families",
    "One Parent Families",
    "No Parent Families",
    "Total Recipients",
    "Adult Recipients",
    "Children Recipients",
]

FAMILY_SHEET_REGEX_PATTERN = re.compile(r"fy(cy)?\d{4}.*families")
RECIPIENT_SHEET_REGEX_PATTERN = re.compile(r"fy(cy)?\d{4}.*recipients")
CASELOAD_FORMAT_OPTIONS = {"number_format": BUILTIN_FORMATS[3]}
CATEGORIES = [
    "Total Families",
    "Two Parent Families",
    "One Parent Families",
    "No Parent Families",
    "Total Recipients",
    "Adult Recipients",
    "Children Recipients",
]

CASELOAD_FOOTNOTES_WIDE = {
    "TANF": [
        [
            "From FY 2002 to FY 2005 Guam's caseload figures reflect an estimate based on the first quarter of FY 2002."
        ]
    ],
    "TANF_SSP": [
        [
            "From FY 2002 to FY 2005 Guam's caseload figures reflect an estimate based on the first quarter of FY 2002."
        ]
    ],
}


CASELOAD_FOOTNOTES_LONG = long_notes("CaseloadData", CASELOAD_FOOTNOTES_WIDE)


def analyze_ambiguous_values(df: pd.DataFrame) -> dict:
    """Display ambiguous values in data frame (0, -, blank)

    Args:
        df (pd.DataFrame): Data frame to analyze

    Returns:
        dict: A dictionary of columns with ambiguous values and the year found
    """

    patterns = {}
    numeric_cols = df.columns.difference(
        ["FiscalYear", "State", "Division", "Funding", "Category"]
    )

    ambiguous_values = {"0", "-", "", " ", np.nan}

    for col in numeric_cols:
        # Filter for only ambiguous values
        values_found = set()
        year_patterns = {}

        for year in sorted(df["FiscalYear"].unique()):
            year_data = df[df["FiscalYear"] == year][col]
            year_ambiguous = {
                str(v).strip()
                for v in year_data.unique()
                if pd.isna(v) or str(v).strip() in ambiguous_values
            }

            if year_ambiguous:
                year_patterns[year] = sorted(year_ambiguous)
                values_found.update(year_ambiguous)

        if values_found:  # Only include columns that have ambiguous values
            patterns[col] = {
                "ambiguous_values_found": sorted(values_found),
                "by_year": year_patterns,
            }

    return patterns


def analyze_guam_data(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and analyze Guam's data

    Args:
        df (pd.DataFrame): Full caseload dataset

    Returns:
        pd.DataFrame: Data frame including only Guam data
    """
    guam_data = df[df["State"].str.contains("Guam", case=False, na=False)].copy()
    guam_data = guam_data.sort_values("FiscalYear")

    # Replace empty strings and whitespace with np.nan for clear missing value identification
    guam_data = guam_data.replace(r"^\s*$", np.nan, regex=True)

    return guam_data


def process_1997_1998_1999_data(
    year: int, df: pd.DataFrame, master_wide: pd.DataFrame
) -> tuple:
    """Process data for years 1997-1999, preserving original value representations."""
    try:
        if year == 1997:
            fiscal_data = pd.DataFrame(
                {
                    "FiscalYear": year,
                    "State": df.iloc[:, 5],  # State column
                    "Total Families": df.iloc[:, 0],  # TOTAL FAMILIES
                    "Two Parent Families": df.iloc[:, 2],  # TANF TWO-PARENT FAMILIES
                    "One Parent Families": df.iloc[:, 3],  # TANF ONE-PARENT FAMILIES
                    "Total Recipients": df.iloc[:, 4],  # TOTAL RECIPIENTS
                }
            )
        else:
            fiscal_data = pd.DataFrame(
                {
                    "FiscalYear": year,
                    "State": df.iloc[:, 4],
                    "Total Families": df.iloc[:, 0],
                    "Two Parent Families": df.iloc[:, 1],
                    "One Parent Families": df.iloc[:, 2],
                    "Total Recipients": df.iloc[:, 3],
                }
            )

        fiscal_data = fiscal_data[fiscal_data["State"].notna()]

        # Add missing columns while preserving original representations
        fiscal_data["No Parent Families"] = None
        fiscal_data["Adult Recipients"] = None
        fiscal_data["Children Recipients"] = None

        fiscal_data = fiscal_data[OUTPUT_COLUMNS]
        fiscal_data = fiscal_data.sort_values(["FiscalYear", "State"]).reset_index(
            drop=True
        )

        return fiscal_data

    except Exception as e:
        print(f"Error processing data for {year}: {e}")
        traceback.print_exc()
        raise


def process_sheet(
    file_path: str, sheet_name: str, column_names: List[str], year: int
) -> Optional[pd.DataFrame]:
    """Load caseload worksheet

    Args:
        file_path (str): Path to caseload workbook
        sheet_name (str): Sheet to load
        skiprows (int): Number of rows to skip
        column_names (List[str]): Names to assign to columns
        year (int): Fiscal year associated with caseload data

    Returns:
        Optional[pd.DataFrame]: Data frame
    """
    try:
        is_old_format = year <= 2020

        if is_old_format:
            # Handling for older formats (2000-2020)
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                skiprows=5,  # Skip rows for old format
                header=None,
                thousands=",",
                dtype={"State": str},
            )

            if "families" in sheet_name.lower():
                df = df[[0, 1, 2, 3, 4]]  # State + family columns
                df.columns = [
                    "State",
                    "Total Families",
                    "Two Parent Families",
                    "One Parent Families",
                    "No Parent Families",
                ]
            else:
                df = df[[0, 1, 2, 3]]  # State + recipient columns
                df.columns = [
                    "State",
                    "Total Recipients",
                    "Adult Recipients",
                    "Children Recipients",
                ]
        else:
            # Handling for standard format (2021+)
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                names=column_names,
                na_values=["--"],
                keep_default_na=False,
                thousands=",",
                dtype={"State": str},
            )
            header = get_header(df, "State", "^State$", idx=True, reset=True)
            df = df.iloc[header + 1 :, :]

        return df

    except Exception as e:
        print(f"Error processing sheet {sheet_name}: {str(e)}")
        print(traceback.format_exc())
        return None


def clean_state(state: str) -> str:
    """Clean up state names

    Args:
        state (str): String state name

    Returns:
        str: String state name
    """
    if state.startswith("Dist"):
        state = "District of Columbia"
    elif state.startswith("U.S. Total"):
        state = "U.S. Total"
    elif state.startswith("Montan"):
        state = "Montana"

    return re.sub(r"/|\d", "", state).strip()


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset

    This function performs the following actions:
        - Clean up State variable
        - Remove rows not containing a state name
        - If "U.S. Total" is not present, generate it by summing all other rows.

    Args:
        df (pd.DataFrame): Data frame to clean

    Returns:
        pd.DataFrame: Cleaned data frame
    """
    df = df.copy()

    # Convert State to string and remove incorrect entries
    df["State"] = df["State"].astype(str).str.strip()
    df["State"] = df["State"].str.replace(r"\*+", "", regex=True)
    df["State"] = df["State"].str.replace('"', "")
    df["State"] = df["State"].apply(clean_state)

    unwanted_patterns = [
        "year",
        r"(?<!guam\s)\d",
        "note",
        "data",
        "source",
        "revised",
        "updated",
        "^as of$",
        r"^\W",
        "'",
        r"^nan",
        "^$",
    ]

    pattern = "|".join(unwanted_patterns)
    mask = ~df["State"].str.lower().str.contains(pattern, regex=True, na=False)
    df = df[mask]

    # Check for the correct number of states
    assert df.shape[0] == 55, "Incorrect number of States!"

    df.dropna(subset=["State"], inplace=True)

    # Check for the correct number of states
    assert df.shape[0] == 55, "Incorrect number of States!"

    return df


def merge_datasets(
    families_df: pd.DataFrame, recipients_df: pd.DataFrame, year: str
) -> pd.DataFrame:
    """Merge families and recipients datasets

    Args:
        families_df (pd.DataFrame): Data frame generated from families tab
        recipients_df (pd.DataFrame): Data frame generated from recipients tab
        year (str): Fiscal year of caseload data

    Returns:
        pd.DataFrame: Merged data frame
    """
    merged = pd.merge(families_df, recipients_df, on="State", how="outer").copy()
    merged.insert(0, "FiscalYear", year)
    return merged


def format_final_dataset(
    df: pd.DataFrame, output_columns: List[str] = OUTPUT_COLUMNS
) -> pd.DataFrame:
    """Format dataset

    This function performs the following actions:
        - Generate columns as NaN if missing
        - Format fiscal year as in integer
        - Add commas to numeric columns
        - Convert column names to title case

    Args:
        df (pd.DataFrame): Data frame to format
        output_columns (List[str]): Columns to include in final dataset

    Returns:
        pd.DataFrame: Formatted data frame
    """
    df = df.copy()

    # Set missing columns to NaN
    for col in output_columns:
        if col not in df.columns:
            df[col] = np.nan

    df = df[output_columns]

    # Format FiscalYear without commas
    if "FiscalYear" in df.columns:
        df["FiscalYear"] = df["FiscalYear"].astype(int)

    df = df.sort_values(["FiscalYear", "State"]).reset_index(drop=True)

    # Format other columns with a comma
    numeric_cols = df.columns.difference(["FiscalYear", "State"])
    df[numeric_cols] = df[numeric_cols].astype(np.float64)

    # Convert all columns to title case
    df.columns = ["FiscalYear"] + [
        col.title() for col in df.columns if col != "FiscalYear"
    ]

    return df


def extract_missing_average(
    path: str, average: str, generate: bool = False
) -> pd.Series:
    workbook = pd.ExcelFile(path)
    sheet_names = workbook.sheet_names

    parameters = {
        "two-parent": {
            "regex": re.compile(r"(two|2)par"),
            "name": "Two Parent Families",
        },
        "one-parent": {
            "regex": re.compile(r"(one|1)par"),
            "name": "One Parent Families",
        },
        "total-family": {
            "regex": re.compile(r"tfam"),
            "name": "Total Families",
        },
        "no-parent": {
            "regex": re.compile(r"(zero|0)par"),
            "name": "No Parent Families",
        },
        "total-recipients": {
            "regex": re.compile(r"trec"),
            "name": "Total Recipients",
        },
        "adult-recipients": {
            "regex": re.compile(r"adults"),
            "name": "Adult Recipients",
        },
        "child-recipients": {
            "regex": re.compile(r"chi?ldre?n"),
            "name": "Children Recipients",
        },
    }
    column_name = parameters[average]["name"]
    sheet_regex = parameters[average]["regex"]
    for sheet in sheet_names:
        sheet_clean = re.sub(r"\W|\s", "", sheet).lower()
        if sheet_regex.match(sheet_clean):
            df = pd.read_excel(workbook, sheet_name=sheet)
            df = get_header(df)
            df = clean_dataset(df)
            # df.columns = df.columns.map(
            #     lambda x: x.strftime("%b-%y") if isinstance(x, datetime) else x
            # )

            if generate:
                df[column_name] = df.iloc[:, 2:13].mean(axis=1)
                return df[["State", column_name]]
            else:
                df.columns = df.columns.map(
                    lambda x: str(x).strip().lower().replace("\n", "")
                )
                columns = df.filter(regex="av.*fy").columns.tolist()
                columns = ["state"] + columns
                return df[columns].rename(
                    columns={"state": "State", columns[1]: column_name}
                )

    return None


if __name__ == "__main__":
    print(
        extract_missing_average(
            "data/original_data/fy2012_ssp_caseload.xls", "one-parent"
        )
    )
