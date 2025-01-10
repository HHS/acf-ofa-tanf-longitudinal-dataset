import re
import traceback
from typing import List, Optional

import numpy as np
import pandas as pd

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


def analyze_ambiguous_values(df: pd.DataFrame) -> dict:
    """
    Analyze only ambiguous values (0, -, blank) in the dataset by column and year.
    Returns patterns dictionary focusing on these specific values.
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
    """
    Extract and analyze Guam's data across all years.
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
        fiscal_data["No Parent Families"] = "-"
        fiscal_data["Adult Recipients"] = "-"
        fiscal_data["Children Recipients"] = "-"

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
    file_path: str, sheet_name: str, skiprows: int, column_names: List[str], year: int
) -> Optional[pd.DataFrame]:
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
                skiprows=skiprows,
                names=column_names,
                na_values=["--"],
                keep_default_na=False,
                thousands=",",
                dtype={"State": str},
            )

        return df

    except Exception as e:
        print(f"Error processing sheet {sheet_name}: {str(e)}")
        print(traceback.format_exc())
        return None


def clean_state(state: str):
    if state.startswith("Dist"):
        state = "District of Columbia"
    elif state.startswith("U.S. Total"):
        state = "U.S. Total"
    elif state.startswith("Montan"):
        state = "Montana"

    return re.sub(r"/|\d", "", state).strip()


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset while preserving original value representations."""
    df = df.copy()

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

    if "U.S. Total" not in df["State"].tolist():
        us_total = df.select_dtypes(include=[np.number]).sum()
        us_total = us_total.to_frame().T
        us_total["State"] = "U.S. Total"
        df = pd.concat([us_total, df])

    assert df.shape[0] == 55, "Incorrect number of States!"

    return df


def merge_datasets(
    families_df: pd.DataFrame, recipients_df: pd.DataFrame, year: str
) -> pd.DataFrame:
    """Merge families and recipients datasets"""
    merged = pd.merge(families_df, recipients_df, on="State", how="outer").copy()
    merged.insert(0, "FiscalYear", year)
    return merged


def fix_fiscal_year_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix the FiscalYear column by removing commas and ensuring integer representation.
    """
    if "FiscalYear" in df.columns:
        df["FiscalYear"] = df["FiscalYear"].astype(str).str.replace(",", "").astype(int)
    return df


def format_final_dataset(df: pd.DataFrame, output_columns: List[str]) -> pd.DataFrame:
    df = df.copy()

    for col in output_columns:
        if col not in df.columns:
            df[col] = np.nan

    df = df[output_columns].copy()

    # Format FiscalYear first, without commas
    if "FiscalYear" in df.columns:
        df["FiscalYear"] = df["FiscalYear"].astype(int)

    numeric_cols = df.columns.difference(["FiscalYear", "State"])
    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", ""), errors="coerce"
        )
        df[col] = df[col].apply(
            lambda x: "{:,}".format(int(x)) if pd.notnull(x) else "-"
        )

    df.columns = ["FiscalYear"] + [
        col.title() for col in df.columns if col != "FiscalYear"
    ]
    return df
