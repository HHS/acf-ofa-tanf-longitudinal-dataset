import pandas as pd
import os
from caseload_FYutils import (
    detect_header_row,
    clean_column_names,
    clean_metadata_rows,
    format_numeric_values,
    merge_tabs,
    reorder_columns,
)

# File paths
files = {
    "Federal": "caseload/data/fy2023_tanf_caseload.xlsx",
    "State": "caseload/data/fy2023_ssp_caseload.xlsx",
    "Total": "caseload/data/fy2023_tanssp_caseload.xlsx",
}

OUTPUT_COLUMNS = [
    "Year", "Month Range", "State", "Total Families", "Two Parent Families",
    "One Parent Families", "No Parent Families", "Total Recipients", "Adults", "Children"
]

def get_sheet_names(file_path):
    """Get actual sheet names from the workbook."""
    try:
        xls = pd.ExcelFile(file_path)
        return xls.sheet_names
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return []

def extract_year_and_month_range(sheet):
    """Extract Year and Month Range from the sheet."""
    try:
        # Look for year in first 5 rows
        for i in range(5):
            row = sheet.iloc[i, 0]
            if isinstance(row, str) and "FY" in row and any(char.isdigit() for char in row):
                year = ''.join(filter(str.isdigit, row))
                # Look for month range in parentheses
                if "(" in row and ")" in row:
                    month_range = row[row.find("(") + 1 : row.find(")")]
                    return year, month_range
        return "2023", "October - September"  # Default values
    except Exception as e:
        print(f"Error extracting year and month range: {str(e)}")
        return "2023", "October - September"

def get_tab_names(sheet_names, data_type):
    """Get the correct tab names based on data type."""
    print(f"\nLooking for sheets in {data_type} data...")
    print(f"Available sheets: {sheet_names}")
    
    if data_type in ["Federal", "Total"]:  # Both use the same tab names
        families_pattern = "FY2023-Families"
        recipients_pattern = "FY2023-Recipients"  # Corrected back to hyphen
    elif data_type == "State":
        families_pattern = "Avg Month Num Fam Oct 22_Sep 23"
        recipients_pattern = "Avg Mo. Num Recipient 2023"
    
    print(f"Looking for patterns: '{families_pattern}' and '{recipients_pattern}'")
    
    # Use exact matching for Federal and Total tabs
    if data_type in ["Federal", "Total"]:
        families_tab = next((s for s in sheet_names if s == families_pattern), None)
        recipients_tab = next((s for s in sheet_names if s == recipients_pattern), None)
    else:
        # Use contains() for State tabs as they might be part of longer names
        families_tab = next((s for s in sheet_names if families_pattern in s), None)
        recipients_tab = next((s for s in sheet_names if recipients_pattern in s), None)
    
    print(f"Found families tab: {families_tab}")
    print(f"Found recipients tab: {recipients_tab}")
    
    return families_tab, recipients_tab

def process_workbook(file_path, data_type):
    """Process a workbook with data type-specific handling."""
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None

        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        
        # Get the correct tab names for this data type
        families_tab, recipients_tab = get_tab_names(sheet_names, data_type)
        if not families_tab or not recipients_tab:
            return None
            
        # Different handling for each data type
        if data_type == "Federal":
            # Read families data starting from row 4 (to include the header)
            families_data = pd.read_excel(
                xls, 
                sheet_name=families_tab, 
                skiprows=4,  # Skip the first 4 rows to get the header
                na_values=['--', '-'],
                keep_default_na=True,
                dtype=str  # Read everything as string first
            )
            
            print("\nDEBUG - Raw families data after correct row skip:")
            print("Columns:", families_data.columns.tolist())
            print(families_data.head())
            
            # Clean column names
            families_data.columns = [
                'State',
                'Total Families',
                'Two Parent Families',
                'One Parent Families',
                'No Parent Families'
            ]
            
            # Convert numeric columns
            for col in families_data.columns:
                if col != 'State':
                    print(f"\nConverting {col}")
                    print("Sample before:", families_data[col].iloc[1:6])  # Skip the header row
                    families_data[col] = (families_data[col]
                                        .astype(str)
                                        .str.replace(',', '')
                                        .str.replace('"', '')
                                        .str.strip())
                    families_data[col] = pd.to_numeric(families_data[col], errors='coerce')
                    print("Sample after:", families_data[col].iloc[1:6])
            
            # Read recipients data starting from row 4
            recipients_data = pd.read_excel(
                xls, 
                sheet_name=recipients_tab, 
                skiprows=4,  # Skip the first 4 rows to get the header
                na_values=['--', '-'],
                keep_default_na=True,
                dtype=str  # Read everything as string first
            )
            
            print("\nDEBUG - Raw recipients data after correct row skip:")
            print("Columns:", recipients_data.columns.tolist())
            print(recipients_data.head())
            
            # Clean column names
            recipients_data.columns = [
                'State',
                'Total Recipients',
                'Adults',
                'Children'
            ]
            
            # Convert numeric columns
            for col in recipients_data.columns:
                if col != 'State':
                    print(f"\nConverting {col}")
                    print("Sample before:", recipients_data[col].iloc[1:6])  # Skip the header row
                    recipients_data[col] = (recipients_data[col]
                                        .astype(str)
                                        .str.replace(',', '')
                                        .str.replace('"', '')
                                        .str.strip())
                    recipients_data[col] = pd.to_numeric(recipients_data[col], errors='coerce')
                    print("Sample after:", recipients_data[col].iloc[1:6])
            
            # Remove the first row (U.S. Totals) from both dataframes
            families_data = families_data[families_data['State'] != 'U.S. Totals']
            recipients_data = recipients_data[recipients_data['State'] != 'U.S. Totals']
                            
        elif data_type == "State":
            families_data = pd.read_excel(
                xls, 
                sheet_name=families_tab, 
                skiprows=5,
                na_values=['--', '-'],
                keep_default_na=True,
                dtype={'State': str}
            )
            recipients_data = pd.read_excel(
                xls, 
                sheet_name=recipients_tab, 
                skiprows=5,
                na_values=['--', '-'],
                keep_default_na=True,
                dtype={'State': str}
            )
        else:  # Total data
            families_data = pd.read_excel(
                xls, 
                sheet_name=families_tab, 
                skiprows=4,
                na_values=['--', '-'],
                keep_default_na=True,
                dtype={'State': str}
            )
            recipients_data = pd.read_excel(
                xls, 
                sheet_name=recipients_tab, 
                skiprows=4,
                na_values=['--', '-'],
                keep_default_na=True,
                dtype={'State': str}
            )

        # Remove any quotation marks or extra whitespace from State column
        families_data['State'] = families_data['State'].str.strip().str.replace('"', '')
        recipients_data['State'] = recipients_data['State'].str.strip().str.replace('"', '')

        # Clean column names if not already cleaned (for State and Total data)
        if data_type != "Federal":
            families_data = clean_column_names(families_data)
            recipients_data = clean_column_names(recipients_data)

        # Clean the data - remove any completely empty rows
        families_data = families_data.dropna(how='all')
        recipients_data = recipients_data.dropna(how='all')

        # Convert numeric columns to float, handling any text values
        numeric_cols = families_data.columns.difference(['State'])
        for col in numeric_cols:
            families_data[col] = pd.to_numeric(
                families_data[col].astype(str).str.replace(',', '').str.strip(), 
                errors='coerce'
            )
            
        numeric_cols = recipients_data.columns.difference(['State'])
        for col in numeric_cols:
            recipients_data[col] = pd.to_numeric(
                recipients_data[col].astype(str).str.replace(',', '').str.strip(), 
                errors='coerce'
            )

        # Extract year and month range
        year = "2023"
        month_range = "October - September"

        # Merge data
        print("\nAttempting to merge data...")
        merged_data = merge_tabs(families_data, recipients_data)
        
        # Add Year and Month Range
        merged_data.insert(0, "Year", year)
        merged_data.insert(1, "Month Range", month_range)

        # Clean metadata rows after merging
        merged_data = clean_metadata_rows(merged_data)
        
        # Format numeric values
        numeric_columns = merged_data.columns.difference(["Year", "Month Range", "State"])
        merged_data = format_numeric_values(merged_data, numeric_columns)
        
        # Ensure all required columns exist
        for col in OUTPUT_COLUMNS:
            if col not in merged_data.columns:
                merged_data[col] = None

        # Reorder columns
        merged_data = reorder_columns(merged_data, OUTPUT_COLUMNS)
        
        print(f"\nFinal data shape: {merged_data.shape}")
        print(f"Sample of final data:\n{merged_data.head()}")
        
        return merged_data

    except Exception as e:
        print(f"\nError processing {file_path} ({data_type}): {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def main():
    results = {}
    
    for data_type, file_path in files.items():
        print(f"\nProcessing {data_type} data...")
        result = process_workbook(file_path, data_type)  # Pass data_type to process_workbook
        if result is not None:
            results[data_type] = result
            print(f"{data_type} data processed successfully.")
        else:
            print(f"Failed to process {data_type} data.")

    if results:
        output_file = "caseload/CaseloadDataLong_Updated.xlsx"
        with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
            for data_type, data in results.items():
                data.to_excel(writer, sheet_name=data_type, index=False)
        print(f"\nUpdated file saved: {output_file}")
    else:
        print("\nNo data was successfully processed.")

if __name__ == "__main__":
    main()