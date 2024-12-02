import pandas as pd
from caseload_utils import (
    detect_header_row,
    reshape_to_long_format,
    reformat_year_column,
    clean_metadata_rows,
    format_numeric_values,
)

# File paths
files = {
    "Federal": "caseload/fy2023_tanf_caseload.xlsx",
    "State": "caseload/fy2023_ssp_caseload.xlsx",
    "Total": "caseload/fy2023_tanssp_caseload.xlsx",
}

# Define tab mappings for each workbook
tabs = {
    "Federal": {
        "TFam": "TANF: Total Number of Families",
        "Two-par": "TANF: Total Number of Two Parent Families",
        "One-par": "TANF: Total Number of One Parent Families",
        "Zero-par": "TANF: Total Number of No Parent Families",
        "TRec": "TANF: Total Number of Recipients",
        "Adults": "TANF: Total Number of Adult Recipients",
        "Children": "TANF: Total Number of Child Recipients",
        "FY2023-Families": "Average Monthly Number of Families",
        "FY2023-Recipients": "Average Monthly Number of Recipients",
    },
    "State": {
        "SSP Total Number of Families": "SSP: Total Number of Families",
        "SSP Total Num 2 Parent Families": "SSP: Total Number of Two Parent Families",
        "SSP Total Num 1 Parent Families": "SSP: Total Number of One Parent Families",
        "SSP Total Num 0 Parent Families": "SSP: Total Number of No Parent Families",
        "SSP Total Number of Recipients": "SSP: Total Number of Recipients",
        "SSP Total Num Adult Recipients": "SSP: Total Number of Adult Recipients",
        "SSP Total Num Child Recipients": "SSP: Total Number of Child Recipients",
        "Avg Month Num Fam Oct 22_Sep 23": "Average Monthly Number of Families",
        "Avg Mo. Num Recipient 2023": "Average Monthly Number of Recipients",
    },
    "Total": {
        "TFam": "TANF&SSP: Total Number of Families",
        "Two-par": "TANF&SSP: Total Number of Two Parent Families",
        "One-par": "TANF&SSP: Total Number of One Parent Families",
        "Zero-par": "TANF&SSP: Total Number of No Parent Families",
        "TRec": "TANF&SSP: Total Number of Recipients",
        "Adults": "TANF&SSP: Total Number of Adult Recipients",
        "Children": "TANF&SSP: Total Number of Child Recipients",
        "FY2023-Families": "Average Monthly Number of Families",
        "FY2023-Recipients": "Average Monthly Number of Recipients",
    },
}

def process_workbook(file_path, tab_mapping, specific_header_row=None):
    """Process Excel workbook into a cleaned DataFrame."""
    dfs = []
    xls = pd.ExcelFile(file_path)
    specific_header_row = specific_header_row or {}

    for sheet_name, variable_name in tab_mapping.items():
        if sheet_name not in xls.sheet_names:
            print(f"Sheet '{sheet_name}' not found in workbook '{file_path}'")
            continue

        try:
            # Load raw data and detect header
            raw_data = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            header = specific_header_row.get(sheet_name, detect_header_row(raw_data))

            if header is None:
                print(f"No valid header found for sheet '{sheet_name}'")
                continue

            # Load data with detected header
            data = pd.read_excel(xls, sheet_name=sheet_name, header=header)

            # Ensure 'State' column exists
            if "State" not in data.columns:
                print(f"'State' column missing in sheet '{sheet_name}'")
                continue

            # Reshape, clean, and reformat
            data = reshape_to_long_format(data)
            data["Variable"] = variable_name
            data = reformat_year_column(data)
            data = clean_metadata_rows(data)
            data = format_numeric_values(data)

            dfs.append(data)
        except Exception as e:
            print(f"Error processing sheet '{sheet_name}': {e}")
            continue

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def main():
    specific_headers = {
        "Avg Month Num Fam Oct 22_Sep 23": 5,
        "Avg Mo. Num Recipient 2023": 5,
    }

    all_data = {}
    for dataset, file_path in files.items():
        all_data[dataset] = process_workbook(file_path, tabs[dataset], specific_headers)

    # Save all datasets into a single Excel file
    output_file = "caseload/CaseloadDataLong_Final.xlsx"
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        for dataset, data in all_data.items():
            data = data[["Year", "State", "Variable", "Value"]]  # Reorder columns
            data.to_excel(writer, sheet_name=dataset, index=False)

    print(f"Processing complete. File saved as '{output_file}'.")

if __name__ == "__main__":
    main()
