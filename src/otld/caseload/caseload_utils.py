import pandas as pd
from typing import List, Optional
import numpy as np
import traceback

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

def analyze_value_patterns(df: pd.DataFrame) -> dict:
    """
    Analyze and document unique value representations in the dataset by column and year.
    Handles mixed types (str, float, null) appropriately.
    Returns patterns dictionary containing unique values and their occurrences by year.
    """
    patterns = {}
    numeric_cols = df.columns.difference(['Fiscal Year', 'State', 'Division', 'Funding', 'Category'])
    
    for col in numeric_cols:
        # Get all unique values and handle them appropriately
        unique_vals = df[col].unique()
        
        # Custom sorting function to handle mixed types
        def sort_mixed_types(x):
            if pd.isna(x):
                return (0, '')  # Nulls first
            if isinstance(x, str):
                if x.strip() == '-':
                    return (1, x)  # Dashes second
                try:
                    # Try to convert string to float for proper numeric sorting
                    return (2, float(x.replace(',', '')))
                except:
                    return (3, x)  # Non-numeric strings last
            return (2, float(x))  # Numbers sorted normally
        
        # Sort unique values using custom function
        sorted_unique = sorted(unique_vals, key=sort_mixed_types)
        
        # Format the values for display
        def format_value(x):
            if pd.isna(x):
                return 'null'
            if isinstance(x, str):
                return x
            if isinstance(x, (int, float)):
                return str(x)
            return str(x)
        
        patterns[col] = {
            'unique_values': [format_value(x) for x in sorted_unique],
            'by_year': {}
        }
        
        # Process values by year
        for year in sorted(df['Fiscal Year'].unique()):
            year_values = df[df['Fiscal Year'] == year][col].unique()
            patterns[col]['by_year'][year] = [
                format_value(x) for x in sorted(year_values, key=sort_mixed_types)
            ]
            
    return patterns

def process_1997_1998_1999_data(year: int, df: pd.DataFrame, master_wide: pd.DataFrame, master_long: pd.DataFrame) -> tuple:
    """Process data for years 1997-1999, preserving original value representations."""
    try:
        if year == 1997:
            fiscal_data = pd.DataFrame({
                'Fiscal Year': year,
                'State': df.iloc[:, 5],  # State column
                'Total Families': df.iloc[:, 0],  # TOTAL FAMILIES
                'Two Parent Families': df.iloc[:, 2],  # TANF TWO-PARENT FAMILIES
                'One Parent Families': df.iloc[:, 3],  # TANF ONE-PARENT FAMILIES
                'Total Recipients': df.iloc[:, 4]  # TOTAL RECIPIENTS
            })
        else:
            fiscal_data = pd.DataFrame({
                'Fiscal Year': year,
                'State': df.iloc[:, 4],  
                'Total Families': df.iloc[:, 0],
                'Two Parent Families': df.iloc[:, 1],
                'One Parent Families': df.iloc[:, 2],
                'Total Recipients': df.iloc[:, 3]
            })
        
        fiscal_data = fiscal_data[fiscal_data['State'].notna()]
        
        # Add missing columns while preserving original representations
        fiscal_data['No Parent Families'] = '-'
        fiscal_data['Adult Recipients'] = '-'
        fiscal_data['Children Recipients'] = '-'
        
        fiscal_data = fiscal_data[OUTPUT_COLUMNS]
        fiscal_data = fiscal_data.sort_values(['Fiscal Year', 'State']).reset_index(drop=True)
        
        master_wide = pd.concat([master_wide, fiscal_data], ignore_index=True)
        
        long_data = pd.melt(
            fiscal_data,
            id_vars=['Fiscal Year', 'State'],
            value_vars=['Total Families', 'Two Parent Families', 'One Parent Families', 'Total Recipients'],
            var_name='Category',
            value_name='Number'
        )
        long_data['Funding'] = 'TANF'
        
        master_long = pd.concat([master_long, long_data], ignore_index=True)
        return master_wide, master_long
        
    except Exception as e:
        print(f"Error processing data for {year}: {e}")
        traceback.print_exc()
        return master_wide, master_long
    except Exception as e:
        print(f"Error processing data for {year}: {e}")
        traceback.print_exc()
        return master_wide, master_long


def process_sheet(file_path: str, sheet_name: str, skiprows: int, 
                 column_names: List[str], is_old_format: bool) -> Optional[pd.DataFrame]:
    try:
        year = int(file_path.split('fy')[1][:4])
        
        if year in [1998, 1999]:
            # Special handling for 1998 and 1999 data
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                skiprows=8,  # Skip rows before the data
                usecols="A:E",  # Select only relevant columns
            )

            # Rename columns
            df.columns = ['State', 'Total Families', 'Two Parent Families', 'One Parent Families', 'Total Recipients']

            # Clean and format
            df = df[df['State'].notna()]
            df['State'] = df['State'].astype(str)
            df = df[~df['State'].str.contains('U.S. Total|Total|download', case=False, na=False)]
            df['Fiscal Year'] = year

            # Add missing columns with NaN or hyphen
            df['No Parent Families'] = np.nan
            df['Adult Recipients'] = np.nan
            df['Children Recipients'] = np.nan

            return df

        if is_old_format:
            # Handling for older formats (2000-2020)
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                skiprows=6,  # Skip rows for old format
                header=None,
                thousands=',',
                dtype={'State': str}
            )

            if 'families' in sheet_name.lower():
                df = df[[0, 1, 2, 3, 4]]  # State + family columns
                df.columns = ['State', 'Total Families', 'Two Parent Families',
                              'One Parent Families', 'No Parent Families']
            else:
                df = df[[0, 1, 2, 3]]  # State + recipient columns
                df.columns = ['State', 'Total Recipients', 'Adult Recipients',
                              'Children Recipients']
        else:
            # Handling for standard format (2021+)
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                skiprows=skiprows,
                names=column_names,
                na_values=['--'],
                keep_default_na=False,
                thousands=',',
                dtype={'State': str}
            )

        return df

    except Exception as e:
        print(f"Error processing sheet {sheet_name}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset while preserving original value representations."""
    df = df.copy()
    
    df['State'] = df['State'].astype(str).str.strip()
    df['State'] = df['State'].str.replace(r'\*+', '', regex=True)
    df['State'] = df['State'].str.replace('"', '')
    
    unwanted_patterns = [
        'U.S. Totals', 'data inapplicable', 'Fiscal year average',
        r'\d{4}-\d{2}-\d{2}', 'As of .*', 'Calendar year average', 
        'Note[s]?:', 'Source:', 'Data as of', 'footnote', '^\d+\.', 
        'See note', 'Revised', 'Updated', r'\d{2}/\d{2}/\d{2,4}', '^As of$'
    ]
    
    pattern = '|'.join(unwanted_patterns)
    mask = ~df['State'].str.contains(pattern, regex=True, na=False)
    return df[mask]

def merge_datasets(families_df: pd.DataFrame, 
                  recipients_df: pd.DataFrame,
                  year: str) -> pd.DataFrame:
    """Merge families and recipients datasets"""
    merged = pd.merge(families_df, recipients_df, on='State', how='outer').copy()
    merged.insert(0, 'Fiscal Year', year)
    return merged

def format_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Format column names to Title Case"""
    df.columns = [col.title() for col in df.columns]
    return df

def fix_fiscal_year_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix the Fiscal Year column by removing commas and ensuring integer representation.
    """
    if 'Fiscal Year' in df.columns:
        df['Fiscal Year'] = df['Fiscal Year'].astype(str).str.replace(',', '').astype(int)
    return df


def format_final_dataset(df: pd.DataFrame, output_columns: List[str]) -> pd.DataFrame:
    df = df.copy()
    
    for col in output_columns:
        if col not in df.columns:
            df[col] = np.nan
    
    df = df[output_columns].copy()
    
    # Format Fiscal Year first, without commas
    if 'Fiscal Year' in df.columns:
        df['Fiscal Year'] = df['Fiscal Year'].astype(int)
    
    numeric_cols = df.columns.difference(['Fiscal Year', 'State'])
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        df[col] = df[col].apply(
            lambda x: "{:,}".format(int(x)) if pd.notnull(x) else "-"
        )
    
    df.columns = [col.title() for col in df.columns]
    return df
