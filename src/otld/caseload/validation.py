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

def validate_values(raw_df: pd.DataFrame, long_df: pd.DataFrame, 
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
                'Long Value': long_value,
                'Match': raw_numeric == long_numeric
            })
    
    return pd.DataFrame(results)

def main():
    args = parse_arguments()
    
    # Load long format data
    long_df = pd.read_excel(args.appended_file)
    
    # Process each raw data file
    validation_results = []
    for data_type, division in TAB_NAMES.items():
        print(f"\nValidating {data_type} data...")
        
        # Process raw data using existing function
        raw_df = process_workbook(os.path.join(args.data_dir, f"fy2023_{division.lower().replace(' ', '')}_caseload.xlsx"), 
                                data_type)
        if raw_df is None:
            continue
            
        # Select random states and metrics
        states = random.sample(raw_df['State'].unique().tolist(), 
                             min(args.sample_size, len(raw_df['State'].unique())))
        metrics = random.sample(CATEGORIES, min(args.sample_size, len(CATEGORIES)))
        
        # Validate values
        results = validate_values(raw_df, long_df, states, metrics, division)
        validation_results.append(results)
        
        # Print results
        print(f"\nValidation results for {division}:")
        print(results)
        
        # Check for mismatches
        mismatches = results[~results['Match']]
        if not mismatches.empty:
            print(f"\nFound {len(mismatches)} mismatches in {division}:")
            print(mismatches)
    
    # Combine and save all results
    if validation_results:
        all_results = pd.concat(validation_results, ignore_index=True)
        output_file = os.path.join(os.path.dirname(args.appended_file), "validation_results.xlsx")
        all_results.to_excel(output_file, index=False)
        print(f"\nValidation results saved to: {output_file}")

if __name__ == "__main__":
    main()