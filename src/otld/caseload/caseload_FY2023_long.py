# caseload_FY2023.py
import pandas as pd
import os
from typing import List, Optional
from caseload_utils import (
    process_sheet,
    clean_dataset,
    merge_datasets,
    format_final_dataset
)

# Configuration
DATA_CONFIGS = {
    "Federal": {
        "skiprows": 4,
        "families_pattern": "-Families",
        "recipients_pattern": "-Recipients",
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
        # Change from list to single pattern that works for both formats
        "families_pattern": "-Families",  # This will match both FYCY and regular patterns
        "recipients_pattern": "-Recipients",
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
        "families_pattern": "-Families",
        "recipients_pattern": "-Recipients",
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
    "Federal": [
        "src/otld/caseload/original_data/fy2023_tanf_caseload.xlsx",
        "src/otld/caseload/original_data/fy2022_tanf_caseload.xlsx",
        "src/otld/caseload/original_data/fy2021_tanf_caseload.xlsx",
        "src/otld/caseload/original_data/fy2020_tanf_caseload.xlsx",
        "src/otld/caseload/original_data/fy2019_tanf_caseload.xlsx",
        "src/otld/caseload/original_data/fy2018_tanf_caseload.xlsx",
        "src/otld/caseload/original_data/fy2017_tanf_caseload.xlsx",
        "src/otld/caseload/original_data/fy2016_tanf_caseload.xls"
    ],
    "State": [
        "src/otld/caseload/original_data/fy2023_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2022_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2021_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2020_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2019_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2018_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2017_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2016_ssp_caseload.xls"
    ],
    "Total": [
        "src/otld/caseload/original_data/fy2023_tanssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2022_tanfssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2021_tanfssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2020_tanfssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2019_tanfssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2018_tanssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2017_tanssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2016_tanssp_caseload.xls"
    ]
}

TAB_NAMES = {
    "Federal": "TANF",
    "State": "SSP-MOE",
    "Total": "TANF and SSP"
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

LONG_FORMAT_COLUMNS = ['Year', 'State', 'Division', 'Category', 'Amount']

def find_matching_sheet(sheet_names: List[str], pattern: str, file_path: str) -> Optional[str]:
    """Find first sheet name that matches pattern, handling special cases"""
    
    # Special case for 2023 State data
    if "2023_ssp" in file_path:
        if "Families" in pattern:
            return next((s for s in sheet_names if "Avg Month Num Fam" in s), None)
        if "Recipients" in pattern:
            return next((s for s in sheet_names if "Avg Mo. Num Recipient" in s), None)
    
    # Handle 2016's spaced pattern
    if "2016" in file_path and "Recipients" in pattern:
        return next((s for s in sheet_names if "FYCY2016 - Recipients" in s), None)
    
    # Standard pattern matching
    return next((s for s in sheet_names 
                if pattern in s.replace(" ", "")), None)

def process_workbook(file_path: str, data_type: str, is_old_format: bool) -> Optional[pd.DataFrame]:
    """Process a single workbook and return the formatted dataset"""
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None

        # Extract year from file path
        year = file_path.split('fy')[1][:4]
        
        config = DATA_CONFIGS[data_type]
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        
        print(f"\nProcessing {data_type} data for {year}")
        print("Looking for sheets matching patterns:")
        print(f"Families pattern: {config['families_pattern']}")
        print(f"Recipients pattern: {config['recipients_pattern']}")
        print(f"Available sheets: {sheet_names}")
        
        families_tab = find_matching_sheet(sheet_names, config["families_pattern"], file_path)
        recipients_tab = find_matching_sheet(sheet_names, config["recipients_pattern"], file_path)
        
        print(f"Found families tab: {families_tab}")
        print(f"Found recipients tab: {recipients_tab}")
        
        if not families_tab or not recipients_tab:
            return None
        
        families_data = process_sheet(
            file_path=file_path,
            sheet_name=families_tab,
            skiprows=config["skiprows"],
            column_names=config["column_mappings"]["families"],
            is_old_format=is_old_format
        )
        
        recipients_data = process_sheet(
            file_path=file_path,
            sheet_name=recipients_tab,
            skiprows=config["skiprows"],
            column_names=config["column_mappings"]["recipients"],
            is_old_format=is_old_format
        )
        
        if families_data is None or recipients_data is None:
            return None

        print(f"Initial data shapes - Families: {families_data.shape}, Recipients: {recipients_data.shape}")
        
        families_data = clean_dataset(families_data)
        recipients_data = clean_dataset(recipients_data)
        
        print(f"Cleaned data shapes - Families: {families_data.shape}, Recipients: {recipients_data.shape}")
        
        # Pass the year to merge_datasets
        merged_data = merge_datasets(families_data, recipients_data, year)
        
        final_data = format_final_dataset(merged_data, OUTPUT_COLUMNS)
        
        print(f"Final data shape: {final_data.shape}")
        
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
    division = long_df['Division'].iloc[0]  # Get the division we're validating
    for state in wide_df['State'].unique():
        for category in CATEGORIES:
            wide_value = wide_df[wide_df['State'] == state][category].iloc[0]
            long_value = long_df[(long_df['State'] == state) & 
                               (long_df['Category'] == category) &
                               (long_df['Division'] == division)]['Amount'].iloc[0]
            
            if wide_value != long_value:
                print(f"Mismatch found for {state} - {category}:")
                print(f"Wide format value: {wide_value}")
                print(f"Long format value: {long_value}")
                return False
    return True

def convert_to_long_format(df: pd.DataFrame, division: str) -> pd.DataFrame:
    """Convert wide format DataFrame to long format with Year, State, Division, Category, Amount columns"""
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
    
    # Add Division column
    long_df.insert(2, 'Division', division)
    
    # Update column order to include Division
    LONG_FORMAT_COLUMNS = ['Year', 'State', 'Division', 'Category', 'Amount']
    
    # Ensure correct column order
    long_df = long_df[LONG_FORMAT_COLUMNS]
    
    # Sort values
    long_df = long_df.sort_values(['State', 'Year', 'Division', 'Category']).reset_index(drop=True)
    
    return long_df

def main():
    # List to collect all results for each tab
    all_results = {
        "TANF": [],
        "SSP-MOE": [],
        "TANF and SSP": []
    }
    
    # Process each file
    for data_type, file_list in FILES.items():
        division_name = TAB_NAMES[data_type]
        
        for file_path in file_list:
            year = file_path.split('fy')[1][:4]
            print(f"\nProcessing {data_type} data for {year}...")
            
            # Determine if this is old format (2016-2020)
            is_old_format = int(year) <= 2020
            
            result = process_workbook(file_path, data_type, is_old_format)
            if result is not None:
                # Add to the appropriate tab's results
                all_results[division_name].append(result)
                print(f"{data_type} data for {year} processed successfully.")
            else:
                print(f"Failed to process {data_type} data for {year}.")

    # Create output directory if it doesn't exist
    os.makedirs("src/otld/caseload/appended_data", exist_ok=True)

    # Combine and save results with proper tabs
    if any(all_results.values()):
        with pd.ExcelWriter("src/otld/caseload/appended_data/CaseloadWide.xlsx", engine="xlsxwriter") as writer:
            for tab_name, results in all_results.items():
                if results:
                    # Combine all results for this tab
                    combined_df = pd.concat(results, ignore_index=True)
                    # Sort by Year and State
                    combined_df = combined_df.sort_values(['Year', 'State']).reset_index(drop=True)
                    # Save to the appropriate tab
                    combined_df.to_excel(writer, sheet_name=tab_name, index=False)
                    print(f"\nSaved {tab_name} tab with shape: {combined_df.shape}")
        
        print("\nWide format file saved: src/otld/caseload/appended_data/CaseloadWide.xlsx")
        
        # Now process and save long format
        all_long_results = []
        for division_name, results in all_results.items():
            if results:
                for df in results:
                    long_result = convert_to_long_format(df, division_name)
                    all_long_results.append(long_result)
        
        if all_long_results:
            combined_long_df = pd.concat(all_long_results, ignore_index=True)
            combined_long_df = combined_long_df.sort_values(['Year', 'State', 'Division', 'Category']).reset_index(drop=True)
            
            long_output_file = "src/otld/caseload/appended_data/CaseloadLong.xlsx"
            combined_long_df.to_excel(long_output_file, index=False)
            print(f"\nLong format file saved: {long_output_file}")
    
    else:
        print("\nNo data was successfully processed.")

if __name__ == "__main__":
    main()