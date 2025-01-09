import pandas as pd
import numpy as np
import os
from typing import List, Optional
from caseload_utils import (
    process_sheet,
    clean_dataset,
    merge_datasets,
    format_final_dataset,
    process_1997_1998_1999_data,
    fix_fiscal_year_column,
    analyze_value_patterns
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

def find_matching_sheet(sheet_names: List[str], pattern: str, file_path: str) -> Optional[str]:
    """Find first sheet name that matches pattern, handling special cases"""
    year = int(file_path.split('fy')[1][:4])

    if year <= 1999:
        return f"FY&CY{str(year)[-2:]}"

    if "2023_ssp" in file_path:
        if "Families" in pattern:
            return next((s for s in sheet_names if "Avg Month Num Fam" in s), None)
        if "Recipients" in pattern:
            return next((s for s in sheet_names if "Avg Mo. Num Recipient" in s), None)

    if year <= 2020:
        if "Families" in pattern:
            possible_families = [
                f"FYCY{year}-Families",
                f"FYCY{year}Families",
                f"fycy{year}-families",
                f"fycy{year}families"
            ]
            for family_pattern in possible_families:
                sheet = next((s for s in sheet_names if family_pattern.lower() in s.lower().replace(" ", "")), None)
                if sheet:
                    return sheet

        if "Recipients" in pattern:
            possible_recipients = [
                f"FYCY{year}-Recipients",
                f"FYCY{year} - Recipients",
                f"FYCY{year}- Recipients",
                f"fycy{year}-recipients",
                f"fycy{year} - recipients",
                f"fycy{year}- recipients"
            ]
            for recipient_pattern in possible_recipients:
                sheet = next((s for s in sheet_names if recipient_pattern.lower() in s.lower()), None)
                if sheet:
                    return sheet

            return next((s for s in sheet_names if f"fycy{year}".lower() in s.lower() and "recipient" in s.lower()), None)

    return next((s for s in sheet_names if pattern in s.replace(" ", "")), None)

def process_workbook(file_path: str, data_type: str, is_old_format: bool, master_wide: pd.DataFrame, master_long: pd.DataFrame) -> Optional[tuple]:
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return master_wide, master_long

        year = int(file_path.split('fy')[1][:4])
        print(f"\nProcessing {data_type} data for {year}...", end='', flush=True)

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

        families_tab = find_matching_sheet(sheet_names, config["families_pattern"], file_path)
        recipients_tab = find_matching_sheet(sheet_names, config["recipients_pattern"], file_path)

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
            return master_wide, master_long

        families_data = clean_dataset(families_data)
        recipients_data = clean_dataset(recipients_data)

        merged_data = merge_datasets(families_data, recipients_data, year)
        if merged_data.empty:
            return master_wide, master_long


        final_data = format_final_dataset(merged_data, OUTPUT_COLUMNS)
        if final_data.empty:
            return master_wide, master_long

        final_data = fix_fiscal_year_column(final_data)  # Ensure Fiscal Year is fixed here
        master_wide = pd.concat([master_wide, final_data], ignore_index=True)

        long_data = pd.melt(
            final_data,
            id_vars=['Fiscal Year', 'State'],
            value_vars=CATEGORIES,
            var_name='Category',
            value_name='Number'
        )
        long_data['Funding'] = data_type
        long_data = fix_fiscal_year_column(long_data)  # Fix Fiscal Year for long format
        master_long = pd.concat([master_long, long_data], ignore_index=True)

        return master_wide, master_long


    except Exception as e:
        print(f"\nError processing {file_path} ({data_type})")
        print(f"Error: {str(e)}")
        return master_wide, master_long

def write_analysis_report(ambiguous_patterns: dict, guam_data: pd.DataFrame, output_file: str):
    """
    Write a focused analysis report including ambiguous value patterns and Guam's data.
    """
    with open(output_file, "w") as f:
        f.write("TANF Caseload Data Analysis Report\n")
        f.write("===============================\n\n")
        
        # Ambiguous Values Section
        f.write("1. Ambiguous Value Patterns\n")
        f.write("-------------------------\n")
        for col, details in ambiguous_patterns.items():
            if details['ambiguous_values_found']:
                f.write(f"\nColumn: {col}\n")
                f.write(f"Ambiguous values found: {details['ambiguous_values_found']}\n")
                f.write("\nOccurrences by year:\n")
                for year, values in sorted(details['by_year'].items()):
                    f.write(f"{year}: {values}\n")
        
        # Guam Section
        f.write("\n\n2. Guam Data Analysis\n")
        f.write("-------------------\n")
        f.write("\nYearly patterns for Guam:\n")
        
        for col in guam_data.columns:
            if col not in ['State', 'Fiscal Year']:
                f.write(f"\n{col}:\n")
                year_values = guam_data.groupby('Fiscal Year')[col].first()
                for year, value in year_values.items():
                    f.write(f"{year}: {value}\n")


def main():
    master_wide = {
        "TANF": pd.DataFrame(columns=OUTPUT_COLUMNS),
        "SSP-MOE": pd.DataFrame(columns=OUTPUT_COLUMNS),
        "TANF and SSP": pd.DataFrame(columns=OUTPUT_COLUMNS)
    }
    master_long = pd.DataFrame(columns=['Fiscal Year', 'State', 'Funding', 'Category', 'Number'])

    # Process all files as before...
    for data_type, file_list in FILES.items():
        for file_path in file_list:
            division_name = TAB_NAMES[data_type]
            result = process_workbook(
                file_path, 
                data_type, 
                int(file_path.split('fy')[1][:4]) <= 2020, 
                master_wide[division_name], 
                master_long
            )
            if result:
                master_wide[division_name], master_long = result

    if any(not df.empty for df in master_wide.values()):
        # Generate focused analysis
        analysis_results = {}
        guam_analysis = {}
        
        for division_name, df in master_wide.items():
            # Analyze ambiguous values
            analysis_results[division_name] = analyze_ambiguous_values(df)
            
            # Extract Guam's data
            guam_analysis[division_name] = analyze_guam_data(df)
        
        # Write focused analysis report
        with open("src/otld/caseload/appended_data/analysis_report.txt", "w") as f:
            f.write("TANF Caseload Data Analysis Report\n")
            f.write("===============================\n\n")
            
            for division_name in master_wide.keys():
                f.write(f"\n{division_name} Division\n")
                f.write("-" * len(f"{division_name} Division") + "\n")
                
                # Write ambiguous value patterns
                patterns = analysis_results[division_name]
                f.write("\nAmbiguous Value Patterns:\n")
                for col, details in patterns.items():
                    if details['ambiguous_values_found']:
                        f.write(f"\n{col}:\n")
                        f.write(f"Values found: {details['ambiguous_values_found']}\n")
                        for year, values in sorted(details['by_year'].items()):
                            if values:
                                f.write(f"{year}: {values}\n")
                
                # Write Guam analysis
                guam_data = guam_analysis[division_name]
                f.write("\nGuam Data Analysis:\n")
                for col in guam_data.columns:
                    if col not in ['State', 'Fiscal Year']:
                        f.write(f"\n{col}:\n")
                        year_values = guam_data.groupby('Fiscal Year')[col].first()
                        for year, value in year_values.items():
                            f.write(f"{year}: {value}\n")
                
                f.write("\n" + "="*50 + "\n")

        # Save the original data files as before...
        with pd.ExcelWriter("src/otld/caseload/appended_data/CaseloadWide.xlsx") as writer:
            for tab_name, df in master_wide.items():
                df = df[df['State'].notna()]
                df = df.sort_values(['Fiscal Year', 'State']).reset_index(drop=True)
                df.to_excel(writer, sheet_name=tab_name, index=False)
        
        # Save Guam data separately
        with pd.ExcelWriter("src/otld/caseload/appended_data/GuamCaseload.xlsx") as writer:
            for division_name, guam_df in guam_analysis.items():
                guam_df.to_excel(writer, sheet_name=division_name, index=False)

if __name__ == "__main__":
    main()