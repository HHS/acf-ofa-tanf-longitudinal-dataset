import os
import re
from typing import List, Optional

import pandas as pd

from otld.utils.caseload_utils import (
    clean_dataset,
    fix_fiscal_year_column,
    format_final_dataset,
    merge_datasets,
    process_1997_1998_1999_data,
    process_sheet,
)

# Configuration
DATA_CONFIGS = {
    "Federal": {
        "skiprows": 4,
        "families_pattern": "-Families",
        "recipients_pattern": "-Recipients",
        "column_mappings": {
            "families": [
                "State",
                "Total Families",
                "Two Parent Families",
                "One Parent Families",
                "No Parent Families",
            ],
            "recipients": [
                "State",
                "Total Recipients",
                "Adult Recipients",
                "Children Recipients",
            ],
        },
    },
    "State": {
        "skiprows": 5,
        # Change from list to single pattern that works for both formats
        "families_pattern": "-Families",  # This will match both FYCY and regular patterns
        "recipients_pattern": "-Recipients",
        "column_mappings": {
            "families": [
                "State",
                "Total Families",
                "Two Parent Families",
                "One Parent Families",
                "No Parent Families",
            ],
            "recipients": [
                "State",
                "Total Recipients",
                "Adult Recipients",
                "Children Recipients",
            ],
        },
    },
    "Total": {
        "skiprows": 4,
        "families_pattern": "-Families",
        "recipients_pattern": "-Recipients",
        "column_mappings": {
            "families": [
                "State",
                "Total Families",
                "Two Parent Families",
                "One Parent Families",
                "No Parent Families",
            ],
            "recipients": [
                "State",
                "Total Recipients",
                "Adult Recipients",
                "Children Recipients",
            ],
        },
    },
}

FILES = {"Federal": [], "State": [], "Total": []}
DATA_DIR = "src/otld/caseload/original_data"
for file in os.listdir(DATA_DIR):
    path = os.path.join(DATA_DIR, file)
    if re.search(r"tanf?_caseload", file):
        FILES["Federal"].append(path)
    elif re.search(r"tanf?ssp_caseload", file):
        FILES["Total"].append(path)
    else:
        FILES["State"].append(path)

TAB_NAMES = {"Federal": "TANF", "State": "SSP-MOE", "Total": "TANF and SSP"}

OUTPUT_COLUMNS = [
    "Fiscal Year",
    "State",
    "Total Families",
    "Two Parent Families",
    "One Parent Families",
    "No Parent Families",
    "Total Recipients",
    "Adult Recipients",
    "Children Recipients",
]

CATEGORIES = [
    "Total Families",
    "Two Parent Families",
    "One Parent Families",
    "No Parent Families",
    "Total Recipients",
    "Adult Recipients",
    "Children Recipients",
]

LONG_FORMAT_COLUMNS = ["Fiscal Year", "State", "Funding", "Category", "Number"]


def find_matching_sheet(
    sheet_names: List[str], pattern: str, file_path: str
) -> Optional[str]:
    """Find first sheet name that matches pattern, handling special cases"""

    # Regex patterns
    family_pattern = re.compile(r"fy(cy)?\d{4}families")
    recipient_pattern = re.compile(r"fy(cy)?\d{4}.*recipients")

    year = int(file_path.split("fy")[1][:4])

    if year <= 1999:
        return f"FY&CY{str(year)[-2:]}"

    if "2023_ssp" in file_path:
        if "Families" in pattern:
            return next((s for s in sheet_names if "Avg Month Num Fam" in s), None)
        if "Recipients" in pattern:
            return next((s for s in sheet_names if "Avg Mo. Num Recipient" in s), None)

    if year <= 2020:
        if "Families" in pattern:
            sheet = next(
                (
                    s
                    for s in sheet_names
                    if family_pattern.search(
                        s.lower().replace(" ", "").replace("-", "")
                    )
                )
            )
            if sheet:
                return sheet
            else:
                raise AttributeError("No matching sheet found!")

        if "Recipients" in pattern:
            sheet = next(
                (
                    s
                    for s in sheet_names
                    if recipient_pattern.search(
                        s.lower().replace(" ", "").replace("-", "")
                    )
                )
            )
            if sheet:
                return sheet
            else:
                raise AttributeError("No matching sheet found!")

    return next((s for s in sheet_names if pattern in s.replace(" ", "")), None)


def process_workbook(
    file_path: str,
    data_type: str,
    is_old_format: bool,
    master_wide: pd.DataFrame,
    master_long: pd.DataFrame,
) -> Optional[tuple]:
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return master_wide, master_long

        year = int(file_path.split("fy")[1][:4])
        print(f"\nProcessing {data_type} data for {year}...", end="", flush=True)

        # Special handling for 1998 and 1999
        if year in [1997, 1998, 1999]:
            try:
                df = pd.read_excel(file_path, skiprows=8, header=None)
                return process_1997_1998_1999_data(year, df, master_wide, master_long)
            except Exception as e:
                print(f"\nError reading {year} data: {e}")
                return master_wide, master_long

        config = DATA_CONFIGS[data_type]
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names

        families_tab = find_matching_sheet(
            sheet_names, config["families_pattern"], file_path
        )
        recipients_tab = find_matching_sheet(
            sheet_names, config["recipients_pattern"], file_path
        )

        if not families_tab or not recipients_tab:
            print("\nFailed to find required sheets. Debug information:")
            print(f"Available sheets: {sheet_names}")
            print(f"Found families tab: {families_tab}")
            print(f"Found recipients tab: {recipients_tab}")
            return master_wide, master_long

        families_data = process_sheet(
            file_path=file_path,
            sheet_name=families_tab,
            skiprows=config["skiprows"],
            column_names=config["column_mappings"]["families"],
            is_old_format=is_old_format,
        )

        recipients_data = process_sheet(
            file_path=file_path,
            sheet_name=recipients_tab,
            skiprows=config["skiprows"],
            column_names=config["column_mappings"]["recipients"],
            is_old_format=is_old_format,
        )

        if families_data is None or recipients_data is None:
            return master_wide, master_long

        families_data = clean_dataset(families_data)
        recipients_data = clean_dataset(recipients_data)

        merged_data = merge_datasets(families_data, recipients_data, year)
        if merged_data.empty:
            return master_wide, master_long

        final_data = format_final_dataset(merged_data, OUTPUT_COLUMNS)
        if final_data.empty:
            return master_wide, master_long

        final_data = fix_fiscal_year_column(
            final_data
        )  # Ensure Fiscal Year is fixed here
        master_wide = pd.concat([master_wide, final_data], ignore_index=True)

        long_data = pd.melt(
            final_data,
            id_vars=["Fiscal Year", "State"],
            value_vars=CATEGORIES,
            var_name="Category",
            value_name="Number",
        )
        long_data["Funding"] = data_type
        long_data = fix_fiscal_year_column(long_data)  # Fix Fiscal Year for long format
        master_long = pd.concat([master_long, long_data], ignore_index=True)

        return master_wide, master_long

    except Exception as e:
        print(f"\nError processing {file_path} ({data_type})")
        print(f"Error: {str(e)}")
        return master_wide, master_long


def main():
    master_wide = {
        "TANF": pd.DataFrame(columns=OUTPUT_COLUMNS),
        "SSP-MOE": pd.DataFrame(columns=OUTPUT_COLUMNS),
        "TANF and SSP": pd.DataFrame(columns=OUTPUT_COLUMNS),
    }
    master_long = pd.DataFrame(
        columns=["Fiscal Year", "State", "Funding", "Category", "Number"]
    )

    # Process all files as before...
    for data_type, file_list in FILES.items():
        for file_path in file_list:
            division_name = TAB_NAMES[data_type]
            result = process_workbook(
                file_path,
                data_type,
                int(file_path.split("fy")[1][:4]) <= 2020,
                master_wide[division_name],
                master_long,
            )
            if result:
                master_wide[division_name], master_long = result

    # Save the original data files as before...
    with pd.ExcelWriter("src/otld/caseload/appended_data/CaseloadWide.xlsx") as writer:
        for tab_name, df in master_wide.items():
            df = df[df["State"].notna()]
            df = df.sort_values(["Fiscal Year", "State"]).reset_index(drop=True)
            df.to_excel(writer, sheet_name=tab_name, index=False)


if __name__ == "__main__":
    main()
