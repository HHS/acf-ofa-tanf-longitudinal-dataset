import pandas as pd
import os
from typing import List, Optional
from caseload_FYutils_refactor import (
    process_sheet,
    clean_dataset,
    merge_datasets,
    format_final_dataset
)

# Configuration
DATA_CONFIGS = {
    "Federal": {
        "skiprows": 3,  # Adjusted to make sure we catch the header row
        "families_pattern": "FY2023-Families",
        "recipients_pattern": "FY2023-Recipients",
        "column_mappings": {
            "families": [
                'State', 'Total Families', 'Two Parent Families',
                'One Parent Families', 'No Parent Families'
            ],
            "recipients": ['State', 'Total Recipients', 'Adult Recipients', 'Children Recipients']
        }
    },
    "State": {
        "skiprows": 5,
        "families_pattern": "Avg Month Num Fam Oct 22_Sep 23",
        "recipients_pattern": "Avg Mo. Num Recipient 2023",
        "column_mappings": {
            "families": [
                'State', 'Total Families', 'Two Parent Families',
                'One Parent Families', 'No Parent Families'
            ],
            "recipients": ['State', 'Total Recipients', 'Adult Recipients', 'Children Recipients']
        }
    },
    "Total": {
        "skiprows": 4,
        "families_pattern": "FY2023-Families",
        "recipients_pattern": "FY2023-Recipients",
        "column_mappings": {
            "families": [
                'State', 'Total Families', 'Two Parent Families',
                'One Parent Families', 'No Parent Families'
            ],
            "recipients": ['State', 'Total Recipients', 'Adult Recipients', 'Children Recipients']
        }
    }
}

FILES = {
    "Federal": "caseload/data/fy2023_tanf_caseload.xlsx",
    "State": "caseload/data/fy2023_ssp_caseload.xlsx",
    "Total": "caseload/data/fy2023_tanssp_caseload.xlsx",
}

TAB_NAMES = {
    "Federal": "TANF",
    "State": "SSP-MOE",
    "Total": "TANF & SSP"
}

OUTPUT_COLUMNS = [
    "Year",
    "State",
    "Total Families",
    "Two Parent Families",
    "One Parent Families",
    "No Parent Families",
    "Total Recipients",
    "Adult Recipients",
    "Children Recipients"
]

def process_workbook(file_path: str, data_type: str) -> Optional[pd.DataFrame]:
    """Process a single workbook and return the formatted dataset"""
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None

        config = DATA_CONFIGS[data_type]
        xls = pd.ExcelFile(file_path)
        
        # Get sheet names
        families_tab = next((s for s in xls.sheet_names 
                           if config["families_pattern"] in s), None)
        recipients_tab = next((s for s in xls.sheet_names 
                             if config["recipients_pattern"] in s), None)
        
        if not families_tab or not recipients_tab:
            print(f"Required sheets not found in {file_path}")
            return None

        # Process individual sheets
        families_data = process_sheet(
            file_path=file_path,
            sheet_name=families_tab,
            skiprows=config["skiprows"],
            column_names=config["column_mappings"]["families"]
        )
        
        recipients_data = process_sheet(
            file_path=file_path,
            sheet_name=recipients_tab,
            skiprows=config["skiprows"],
            column_names=config["column_mappings"]["recipients"]
        )
        
        if families_data is None or recipients_data is None:
            return None

        # Clean datasets
        families_data = clean_dataset(families_data)
        recipients_data = clean_dataset(recipients_data)
        
        # Merge and format
        merged_data = merge_datasets(families_data, recipients_data)
        final_data = format_final_dataset(merged_data, OUTPUT_COLUMNS)
        
        return final_data

    except Exception as e:
        print(f"Error processing {file_path} ({data_type}): {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def main():
    # Process each workbook
    results = {}
    for data_type, file_path in FILES.items():
        print(f"\nProcessing {data_type} data...")
        result = process_workbook(file_path, data_type)
        if result is not None:
            results[data_type] = result
            print(f"{data_type} data processed successfully.")
        else:
            print(f"Failed to process {data_type} data.")

    # Save results with renamed tabs
    if results:
        output_file = "caseload/CaseloadDataWide_refactor.xlsx"
        with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
            for data_type, data in results.items():
                tab_name = TAB_NAMES[data_type]
                data.to_excel(writer, sheet_name=tab_name, index=False)
                print(f"Saved {data_type} data to tab '{tab_name}'")
        print(f"\nUpdated file saved: {output_file}")
    else:
        print("\nNo data was successfully processed.")

if __name__ == "__main__":
    main()