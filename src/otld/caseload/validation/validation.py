# validate_caseload.py
import pandas as pd
import os
import argparse
import random
from typing import Dict, List, Optional
from caseload_utils import (
    process_sheet,
    clean_dataset,
    merge_datasets,
    format_final_dataset
)
from caseload_FY2023_long import (
    DATA_CONFIGS,
    TAB_NAMES,
    CATEGORIES,
    process_workbook
)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Validate caseload data between raw files and appended format.')
    parser.add_argument('--data-dir', required=True,
                       help='Directory containing raw data files')
    parser.add_argument('--appended-file', required=True,
                       help='Path to appended file (Long or Wide format)')
    parser.add_argument('--sample-size', type=int, default=5,
                       help='Number of random state-metric combinations to validate')
    return parser.parse_args()

def validate_long_format(raw_df: pd.DataFrame, long_df: pd.DataFrame, 
                        states: List[str], metrics: List[str], division: str) -> pd.DataFrame:
    """Compare values between raw and long format for selected states and metrics"""
    results = []
    
    for state in states:
        for metric in metrics:
            raw_value = raw_df[raw_df['State'] == state][metric].iloc[0]
            long_value = long_df[
                (long_df['State'] == state) & 
                (long_df['Category'] == metric) & 
                (long_df['Division'] == division)
            ]['Amount'].iloc[0]
            
            # Convert to numeric for comparison
            raw_numeric = pd.to_numeric(str(raw_value).replace(',', ''))
            long_numeric = pd.to_numeric(str(long_value).replace(',', ''))
            
            results.append({
                'State': state,
                'Division': division,
                'Metric': metric,
                'Raw Value': raw_value,
                'Formatted Value': long_value,
                'Match': raw_numeric == long_numeric
            })
    
    return pd.DataFrame(results)

def validate_wide_format(raw_df: pd.DataFrame, wide_df: pd.DataFrame, 
                        states: List[str], metrics: List[str], division: str) -> pd.DataFrame:
    """Compare values between raw and wide format for selected states and metrics"""
    results = []
    
    print(f"\nValidating {division} data...")
    
    for state in states:
        for metric in metrics:
            raw_value = raw_df[raw_df['State'] == state][metric].iloc[0]
            column_name = metric
            
            if column_name not in wide_df.columns:
                print(f"Warning: Could not find column '{column_name}' in wide format")
                continue
                
            wide_value = wide_df[
                wide_df['State'] == state
            ][column_name].iloc[0]
            
            # Convert string values to integers for comparison
            try:
                raw_int = int(str(raw_value).replace(',', ''))
                wide_int = int(str(wide_value).replace(',', ''))
                is_match = raw_int == wide_int
                difference = raw_int - wide_int if not is_match else 0
            except (ValueError, TypeError):
                is_match = str(raw_value).strip() == str(wide_value).strip()
                difference = None
            
            results.append({
                'State': state,
                'Division': division,
                'Metric': metric,
                'Raw Value': raw_value,
                'Formatted Value': wide_value,
                'Difference': difference,
                'Match': is_match,
                'Column Used': column_name,
                'Note': get_note(division, is_match)
            })
    
    # Only show mismatches in the summary
    results_df = pd.DataFrame(results)
    mismatches = results_df[~results_df['Match']]
    
    if not mismatches.empty:
        print(f"\nFound {len(mismatches)} mismatches in {division}:")
        print(mismatches[['State', 'Metric', 'Raw Value', 'Formatted Value', 'Difference']])
    else:
        print(f"All validations passed for {division}.")

    return results_df

def get_note(division: str, is_match: bool) -> str:
    """Get appropriate note based on division and match status"""
    if not is_match:
        if division == 'SSP-MOE':
            return "SSP-MOE data may be combined with TANF in wide format"
        elif division == 'TANF and SSP':
            return "Combined totals may include additional calculations"
    return ""

def validate_values(raw_df: pd.DataFrame, formatted_df: pd.DataFrame, 
                   states: List[str], metrics: List[str], division: str) -> pd.DataFrame:
    """Route validation to appropriate function based on format"""
    # Load the correct tab from the formatted file based on division
    if isinstance(formatted_df, pd.ExcelFile):
        formatted_df = formatted_df.parse(division)
    
    return validate_wide_format(raw_df, formatted_df, states, metrics, division)

def main():
    args = parse_arguments()
    
    # Load wide format data as ExcelFile to access all tabs
    wide_df = pd.ExcelFile(args.appended_file)
    
    # Process each raw data file
    validation_results = []
    for data_type, division in TAB_NAMES.items():
        print(f"\nValidating {data_type} data...")
        
        # Map the division names to actual filenames
        filename_map = {
            'TANF': 'tanf',
            'SSP-MOE': 'ssp',
            'TANF and SSP': 'tanssp'
        }
        
        # Get the correct filename suffix
        file_suffix = filename_map.get(division, division.lower())
        filename = f"fy2023_{file_suffix}_caseload.xlsx"
        filepath = os.path.join(args.data_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
            
        # Process raw data using existing function
        raw_df = process_workbook(filepath, data_type)
        if raw_df is None:
            continue
            
        # Select random states and metrics
        states = random.sample(raw_df['State'].unique().tolist(), 
                             min(args.sample_size, len(raw_df['State'].unique())))
        metrics = random.sample(CATEGORIES, min(args.sample_size, len(CATEGORIES)))
        
        # Validate values using the correct tab
        results = validate_values(raw_df, wide_df, states, metrics, division)
        validation_results.append(results)
    
    # Save results to Excel
    if validation_results:
        all_results = pd.concat(validation_results, ignore_index=True)
        output_file = os.path.join(os.path.dirname(args.appended_file), "validation_results.xlsx")
        all_results.to_excel(output_file, index=False)
        print(f"\nValidation results saved to: {output_file}")

if __name__ == "__main__":
    main()