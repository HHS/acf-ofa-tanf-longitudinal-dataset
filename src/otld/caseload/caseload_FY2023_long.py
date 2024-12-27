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
import traceback

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
        "src/otld/caseload/original_data/fy2016_tanf_caseload.xls",
        "src/otld/caseload/original_data/fy2015_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2014_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2013_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2012_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2011_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2010_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2009_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2008_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2007_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2006_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2005_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2004_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2003_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2002_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2001_tan_caseload.xls",
        "src/otld/caseload/original_data/fy2000_tan_caseload.xls",
        "src/otld/caseload/original_data/fy1999_tan_caseload.xls",
        "src/otld/caseload/original_data/fy1998_tan_caseload.xls",
        "src/otld/caseload/original_data/fy1997_tan_caseload.xls"
    ],
    "State": [
        "src/otld/caseload/original_data/fy2023_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2022_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2021_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2020_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2019_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2018_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2017_ssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2016_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2015_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2014_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2013_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2012_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2011_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2010_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2009_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2008_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2007_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2006_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2005_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2004_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2003_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2002_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2001_ssp_caseload.xls",
        "src/otld/caseload/original_data/fy2000_ssp_caseload.xls",
    ],
    "Total": [
        "src/otld/caseload/original_data/fy2023_tanssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2022_tanfssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2021_tanfssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2020_tanfssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2019_tanfssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2018_tanssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2017_tanssp_caseload.xlsx",
        "src/otld/caseload/original_data/fy2016_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2015_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2014_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2013_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2012_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2011_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2010_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2009_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2008_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2007_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2006_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2005_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2004_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2003_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2002_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2001_tanssp_caseload.xls",
        "src/otld/caseload/original_data/fy2000_tanssp_caseload.xls",

    ]
}

TAB_NAMES = {
    "Federal": "TANF",
    "State": "SSP-MOE",
    "Total": "TANF and SSP"
}

OUTPUT_COLUMNS = [
    "Fiscal Year",
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

LONG_FORMAT_COLUMNS = ['Fiscal Year', 'State', 'Funding', 'Category', 'Number']

# for years 1997-2023
def find_matching_sheet(sheet_names: List[str], pattern: str, file_path: str) -> Optional[str]:
    """Find first sheet name that matches pattern, handling special cases"""
    
    # Get the year from the file path
    year = file_path.split('fy')[1][:4]

    if int(year) <= 1999:
        return f"FY&CY{year[-2:]}"
    
    # Special case for 2023 State data
    if "2023_ssp" in file_path:
        if "Families" in pattern:
            return next((s for s in sheet_names if "Avg Month Num Fam" in s), None)
        if "Recipients" in pattern:
            return next((s for s in sheet_names if "Avg Mo. Num Recipient" in s), None)
    
    # For years 2001-2020, use case-insensitive and flexible pattern matching
    if int(year) <= 2020:
        if "Families" in pattern:
            # Try all variations for Families sheets
            possible_families = [
                f"FYCY{year}-Families",     # Standard format uppercase
                f"FYCY{year}Families",      # No hyphen uppercase
                f"fycy{year}-families",     # Standard format lowercase
                f"fycy{year}families"       # No hyphen lowercase
            ]
            
            # Try each pattern with case-insensitive matching
            for family_pattern in possible_families:
                sheet = next((s for s in sheet_names 
                            if family_pattern.lower() in s.lower().replace(" ", "")), None)
                if sheet:
                    return sheet
                
        if "Recipients" in pattern:
            # Try all variations for Recipients sheets
            possible_recipients = [
                f"FYCY{year}-Recipients",       # Standard format uppercase
                f"FYCY{year} - Recipients",     # Spaced format uppercase
                f"FYCY{year}- Recipients",      # Mixed format uppercase
                f"fycy{year}-recipients",       # Standard format lowercase
                f"fycy{year} - recipients",     # Spaced format lowercase
                f"fycy{year}- recipients"       # Mixed format lowercase
            ]
            
            # Try each pattern with case-insensitive matching
            for recipient_pattern in possible_recipients:
                sheet = next((s for s in sheet_names 
                            if recipient_pattern.lower() in s.lower()), None)
                if sheet:
                    return sheet
                    
            # If still not found, try more flexible matching
            return next((s for s in sheet_names 
                        if f"fycy{year}".lower() in s.lower() and "recipient" in s.lower()), None)
    
    # Standard pattern matching for 2021+
    return next((s for s in sheet_names 
                if pattern in s.replace(" ", "")), None)


def process_workbook(file_path: str, data_type: str, is_old_format: bool) -> Optional[pd.DataFrame]:
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None

        year = file_path.split('fy')[1][:4]
        print(f"\nProcessing {data_type} data for {year}...", end='', flush=True)

        config = DATA_CONFIGS[data_type]
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        
        families_tab = find_matching_sheet(sheet_names, config["families_pattern"], file_path)
        recipients_tab = find_matching_sheet(sheet_names, config["recipients_pattern"], file_path)
        
        if not families_tab or not recipients_tab:
            print("\nFailed to find required sheets. Debug information:")
            print(f"Available sheets: {sheet_names}")
            print(f"Found families tab: {families_tab}")
            print(f"Found recipients tab: {recipients_tab}")
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

        families_data = clean_dataset(families_data)
        recipients_data = clean_dataset(recipients_data)

        merged_data = merge_datasets(families_data, recipients_data, year)
        if merged_data.empty:
            return None

        final_data = format_final_dataset(merged_data, OUTPUT_COLUMNS)
        if final_data.empty:
            return None

        # Convert Fiscal Year column to integer
        final_data['Fiscal Year'] = final_data['Fiscal Year'].astype(int)

        print(" Success!")
        return final_data

    except Exception as e:
        print(f"\nError processing {file_path} ({data_type})")
        print(f"Error: {str(e)}")
        traceback.print_exc()
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
    results_by_division = {
        "TANF": [],
        "SSP-MOE": [],
        "TANF and SSP": []
    }
    
    for data_type, file_list in FILES.items():
        division_name = TAB_NAMES[data_type]
        
        for file_path in file_list:
            result = process_workbook(file_path, data_type, int(file_path.split('fy')[1][:4]) <= 2020)
            if result is not None:
                result['Division'] = division_name
                # Format Fiscal Year without commas
                result['Fiscal Year'] = result['Fiscal Year'].map(lambda x: '{:d}'.format(int(x)))
                results_by_division[division_name].append(result)

    if any(results_by_division.values()):
        # Process wide format
        with pd.ExcelWriter("src/otld/caseload/appended_data/CaseloadWide.xlsx") as writer:
            for division_name, division_results in results_by_division.items():
                if division_results:
                    df = pd.concat(division_results, ignore_index=True)
                    df = clean_dataset(df)
                    df = df.drop('Division', axis=1)
                    # Format Fiscal Year without commas
                    df['Fiscal Year'] = df['Fiscal Year'].map(lambda x: '{:d}'.format(int(x)))
                    df = df.sort_values(['Fiscal Year', 'State']).reset_index(drop=True)
                    df.to_excel(writer, sheet_name=division_name, index=False)
        
        # Process long format
        all_long_results = []
        for division_name, division_results in results_by_division.items():
            for df in division_results:
                long_df = pd.melt(
                    df,
                    id_vars=['Fiscal Year', 'State', 'Division'],
                    value_vars=CATEGORIES,
                    var_name='Category',
                    value_name='Number'
                )
                long_df = long_df.rename(columns={'Division': 'Funding'})
                all_long_results.append(long_df)

        combined_long_df = pd.concat(all_long_results, ignore_index=True)
        combined_long_df = combined_long_df.sort_values(['Fiscal Year', 'State', 'Funding', 'Category']).reset_index(drop=True)
        combined_long_df.to_excel(
            "src/otld/caseload/appended_data/CaseloadLong.xlsx",
            sheet_name="1998-2023 TANF Caseloads",
            index=False
        )
    else:
        print("\nNo data was successfully processed.")

if __name__ == "__main__":
    main()