# caseload_FY2023.py
import pandas as pd
import os
from typing import Dict, Optional
from caseload_FYutils_refactor import (
    process_sheet,
    clean_dataset,
    merge_datasets,
    format_final_dataset
)

# Configuration
DATA_CONFIGS = {
    "Federal": {
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

CATEGORIES = [
    'Total Families',
    'Two Parent Families',
    'One Parent Families',
    'No Parent Families',
    'Total Recipients',
    'Adult Recipients',
    'Children Recipients'
]

LONG_FORMAT_COLUMNS = ['Year', 'State', 'Category', 'Amount']

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

def validate_conversion(wide_df: pd.DataFrame, long_df: pd.DataFrame) -> bool:
    """
    Validate that the wide to long conversion maintained data integrity
    Returns True if validation passes, False otherwise
    """
    for state in wide_df['State'].unique():
        for category in CATEGORIES:
            wide_value = wide_df[wide_df['State'] == state][category].iloc[0]
            long_value = long_df[(long_df['State'] == state) & 
                               (long_df['Category'] == category)]['Amount'].iloc[0]
            
            if wide_value != long_value:
                print(f"Mismatch found for {state} - {category}:")
                print(f"Wide format value: {wide_value}")
                print(f"Long format value: {long_value}")
                return False
    return True

def convert_to_long_format(df: pd.DataFrame) -> pd.DataFrame:
    """Convert wide format DataFrame to long format with Year, State, Category, Amount columns"""
    # Make a copy of the input DataFrame to avoid modifications
    df = df.copy()
    
    # Melt the DataFrame to create long format
    long_df = pd.melt(
        df,
        id_vars=['Year', 'State'],
        value_vars=CATEGORIES,
        var_name='Category',
        value_name='Amount'
    )
    
    # Ensure correct column order
    long_df = long_df[LONG_FORMAT_COLUMNS]
    
    # Sort values
    long_df = long_df.sort_values(['State', 'Year', 'Category']).reset_index(drop=True)
    
    # Validate the conversion
    if not validate_conversion(df, long_df):
        print("Warning: Data validation failed!")
    
    return long_df

def main():
    # Process each workbook
    results = {}
    for data_type, file_path in FILES.items():
        print(f"\nProcessing {data_type} data...")
        result = process_workbook(file_path, data_type)
        if result is not None:
            # Store wide format for validation
            wide_result = result.copy()
            
            # Convert to long format
            long_result = convert_to_long_format(result)
            
            # Additional validation check
            print(f"\nValidating {data_type} data conversion...")
            if validate_conversion(wide_result, long_result):
                print("Validation passed!")
                results[data_type] = long_result
                print(f"{data_type} data processed successfully.")
            else:
                print(f"Warning: Validation failed for {data_type} data!")
        else:
            print(f"Failed to process {data_type} data.")

    # Save results with renamed tabs
    if results:
        output_file = "caseload/CaseloadDataLong_Updated.xlsx"
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