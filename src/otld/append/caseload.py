import os
import re
from typing import List, Optional

import pandas as pd

from otld.paths import out_dir, tableau_dir
from otld.utils import export_workbook, get_header
from otld.utils.caseload_utils import (
    clean_dataset,
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

TAB_NAMES = {"Federal": "TANF", "State": "SSP_MOE", "Total": "TANF_SSP"}

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

CATEGORIES = [
    "Total Families",
    "Two Parent Families",
    "One Parent Families",
    "No Parent Families",
    "Total Recipients",
    "Adult Recipients",
    "Children Recipients",
]

LONG_FORMAT_COLUMNS = ["FiscalYear", "State", "Funding", "Category", "Number"]


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
    year: int,
    master_wide: pd.DataFrame,
) -> Optional[tuple]:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")

        print(f"\nProcessing {data_type} data for {year}...", end="", flush=True)

        # Special handling for 1998 and 1999
        if year in [1997, 1998, 1999]:
            try:
                df = pd.read_excel(file_path, header=None)
                index = get_header(df, 0, "total", sanitize=True, idx=True)
                df = df.iloc[index + 1 :, :]
                df = process_1997_1998_1999_data(year, df, master_wide)
                df = clean_dataset(df)
                df = format_final_dataset(df, OUTPUT_COLUMNS)
                return pd.concat([master_wide, df])
            except Exception as e:
                print(f"\nError reading {year} data: {e}")
                raise

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
            raise AttributeError(
                f"A tab is missing!\nFamilies: {families_tab};\nRecipients: {recipients_tab}"
            )

        families_data = process_sheet(
            file_path=file_path,
            sheet_name=families_tab,
            skiprows=config["skiprows"],
            column_names=config["column_mappings"]["families"],
            year=year,
        )

        recipients_data = process_sheet(
            file_path=file_path,
            sheet_name=recipients_tab,
            skiprows=config["skiprows"],
            column_names=config["column_mappings"]["recipients"],
            year=year,
        )

        if families_data is None or recipients_data is None:
            raise AttributeError(
                f"At least one sheet is missing:\nFamilies: {families_data}\nRecipients: {recipients_data}"
            )

        if year == 2004 and data_type == "State":
            assert families_data["State"].loc[53] == "As of 9/21/2006"
            assert recipients_data["State"].loc[53] == "As of 9/21/2006"

            for df in [families_data, recipients_data]:
                df["State"] = df["State"].apply(
                    lambda x: "Wisconsin" if x == "As of 9/21/2006" else x
                )

        families_data = clean_dataset(families_data)
        recipients_data = clean_dataset(recipients_data)

        merged_data = merge_datasets(families_data, recipients_data, year)
        if merged_data.empty:
            return master_wide

        final_data = format_final_dataset(merged_data, OUTPUT_COLUMNS)
        if final_data.empty:
            return master_wide

        master_wide = pd.concat([master_wide, final_data], ignore_index=True)

        return master_wide

    except Exception as e:
        print(f"\nError processing {file_path} ({data_type})")
        print(f"Error: {str(e)}")
        raise


def main():
    master_wide = {
        tab: pd.DataFrame(columns=OUTPUT_COLUMNS) for tab in TAB_NAMES.values()
    }

    # Process all files as before...
    for data_type, file_list in FILES.items():
        for file_path in file_list:
            year = int(file_path.split("fy")[1][:4])
            division_name = TAB_NAMES[data_type]
            # if year != 2004 or division_name != "SSP-MOE":
            #     continue
            master_wide[division_name] = process_workbook(
                file_path,
                data_type,
                year,
                master_wide[division_name],
            )

    for frame in master_wide:
        master_wide[frame].set_index(["State", "FiscalYear"], inplace=True)

    # Save the original data files as before...
    export_workbook(master_wide, os.path.join(out_dir, "CaseloadDataWide.xlsx"))
    export_workbook(master_wide, "src/otld/caseload/appended_data/CaseloadWide.xlsx")

    master_wide["CaseloadData"] = []
    for frame in master_wide:
        if frame == "CaseloadData":
            continue
        master_wide[frame] = master_wide[frame].melt(
            value_vars=CATEGORIES,
            var_name="Category",
            value_name="Number",
            ignore_index=False,
        )
        master_wide[frame]["Funding"] = frame
        master_wide["CaseloadData"].append(master_wide[frame])

    master_wide["CaseloadData"] = pd.concat(master_wide["CaseloadData"])
    for frame in list(master_wide.keys()):
        if frame != "CaseloadData":
            del master_wide[frame]

    export_workbook(
        master_wide, os.path.join(tableau_dir, "data", "CaseloadDataLongRaw.xlsx")
    )
    export_workbook(master_wide, os.path.join(out_dir, "CaseloadDataLong.xlsx"))
    export_workbook(master_wide, "src/otld/caseload/appended_data/CaseloadLong.xlsx")


if __name__ == "__main__":
    main()
