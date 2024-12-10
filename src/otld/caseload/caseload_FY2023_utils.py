import pandas as pd
from datetime import datetime

def detect_header_row(raw_data, keywords=["State", "STATE", "state"]):
    """Detect the header row containing any of the specified keywords."""
    for keyword in keywords:
        header_row = raw_data.astype(str).apply(
            lambda row: row.str.contains(keyword, case=False, na=False).any(), axis=1
        )
        if header_row.any():
            return header_row.idxmax()
    
    # If no header found, try to find a row with common column names
    common_columns = ["Total", "Families", "Recipients", "Adults", "Children"]
    for i in range(min(10, len(raw_data))):  # Check first 10 rows
        row_values = raw_data.iloc[i].astype(str)
        if any(col in ' '.join(row_values) for col in common_columns):
            return i
    
    return 0  # Default to first row if no header found


def clean_column_names(data):
    """Clean and normalize column names by stripping extra spaces and newlines."""
    data.columns = (
        data.columns.str.replace("\n", " ", regex=True)  # Replace newlines
                       .str.replace("\s+", " ", regex=True)  # Collapse multiple spaces
                       .str.strip()  # Trim leading/trailing spaces
    )
    return data

def clean_metadata_rows(data, state_column="State"):
    """Remove rows with metadata or notes."""
    unwanted_keywords = [
        "Notes", "Fiscal year average", "data inapplicable",
        "Total", "Source", "Prepared", "Report"
    ]
    
    # Convert state column to string and handle NaN values
    data[state_column] = data[state_column].astype(str)
    
    # Remove rows containing unwanted keywords
    mask = ~data[state_column].str.contains(
        "|".join(unwanted_keywords), 
        case=False, 
        na=False
    )
    
    # Remove rows where state is empty or just whitespace
    mask &= data[state_column].str.strip().str.len() > 0
    
    # Remove rows where state contains numbers (likely headers or footers)
    mask &= ~data[state_column].str.contains(r'\d')
    
    return data[mask]

def format_numeric_values(data, numeric_columns):
    """Format numeric values with commas for thousands separators."""
    for column in numeric_columns:
        data[column] = data[column].apply(
            lambda x: "{:,.0f}".format(x) if pd.notnull(x) and isinstance(x, (int, float)) else x
        )
    return data

def merge_tabs(families_data, recipients_data):
    """Merge Families and Recipients tabs into one DataFrame."""
    merged_data = families_data.merge(
        recipients_data, on="State", suffixes=("_Families", "_Recipients")
    )
    return merged_data

def select_relevant_columns(data, columns):
    """Select only relevant columns for the output."""
    return data[columns]

def add_year_column(data, year):
    """Add a fixed 'Year' column to the DataFrame."""
    data.insert(0, "Year", year)
    return data

def reorder_columns(data, column_order):
    """Reorder columns in the DataFrame."""
    return data[column_order]
