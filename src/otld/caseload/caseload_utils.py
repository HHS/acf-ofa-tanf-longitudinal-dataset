import pandas as pd
from typing import List, Optional


def process_sheet(file_path: str, sheet_name: str, skiprows: int, 
                 column_names: List[str], is_old_format: bool) -> Optional[pd.DataFrame]:
    """Read and process a single Excel sheet"""
    try:
        if is_old_format:
            # For 2001-2020 data, we need to handle fiscal year columns specifically
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                skiprows=6,  # Skip 6 rows for old format
                header=None,  # Don't use first row as header
                thousands=',',
                dtype={'State': str}
            )
            
            # Extract only the fiscal year columns (first set of data columns)
            if 'families' in sheet_name.lower():
                df = df[[0, 1, 2, 3, 4]]  # State + 4 family columns
                df.columns = ['State', 'Total Families', 'Two Parent Families',
                            'One Parent Families', 'No Parent Families']
            else:  # Recipients sheet
                df = df[[0, 1, 2, 3]]  # State + 3 recipient columns
                df.columns = ['State', 'Total Recipients', 'Adult Recipients',
                            'Children Recipients']
        else:
            # For 2021+ data, use the standard format
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
    """Clean a dataset by handling state names and numeric columns"""
    df = df.copy()
    
    # Clean state names
    df['State'] = df['State'].astype(str).str.strip()
    df['State'] = df['State'].str.replace(r'\*+', '', regex=True)  # Remove asterisks
    df['State'] = df['State'].str.replace('"', '')
    
    # Filter out unwanted rows - expanded patterns for notes and dates
    unwanted_patterns = [
        'U.S. Totals',
        'data inapplicable',
        'Fiscal year average',
        r'\d{4}-\d{2}-\d{2}',
        '^\s*$',
        '^-',
        'As of \d{2}/\d{2}/\d{4}',     # Matches "As of MM/DD/YYYY"
        'As of \d{2}/\d{2}/\d{2}',      # Matches "As of MM/DD/YY"
        'As of.*',                       # Matches any "As of" text with following content
        'Calendar year average',         # Matches calendar year notes
        'Note[s]?:',                     # Matches both "Note:" and "Notes:"
        'Source:',                       # Matches source citations
        'Data as of',                    # Matches date stamps
        'footnote',                      # Matches footnote references
        '^\d+\.',                        # Matches numbered notes
        'See note',                      # Matches note references
        'Revised',                       # Matches revision notes
        'Updated',                       # Matches update notes
        r'\d{2}/\d{2}/\d{2,4}',         # Matches any date format
        r'^\d{4}$',                      # Matches year-only entries
        '^As of$',                       # Matches standalone "As of"
    ]
    
    pattern = '|'.join(unwanted_patterns)
    mask = ~df['State'].str.contains(pattern, regex=True, na=False)
    df = df[mask].copy()
    
    # Additional filtering for state names
    df = df[df['State'].str.len() <= 50]  # Filter out long text that might be notes
    df = df[~df['State'].str.contains(r'\d{4}')]  # Filter out anything with years in it
    
    # Filter out rows where State column contains any variant of "As of" case-insensitive
    df = df[~df['State'].str.lower().str.contains('as of')]
    
    # Filter out rows where all numeric columns are 0
    numeric_cols = df.columns.difference(['State'])
    all_zeros = df[numeric_cols].apply(lambda x: pd.to_numeric(x, errors='coerce')).fillna(0).eq(0).all(axis=1)
    df = df[~(all_zeros & df['State'].str.lower().str.contains('note|source|data|see|revised|updated|as of'))]
    
    # Clean numeric columns
    for col in numeric_cols:
        if df[col].dtype == 'object':
            temp_series = (df[col].astype(str)
                         .str.strip()
                         .str.replace(',', '')
                         .str.replace('"', '')
                         .str.replace('***', '')
                         .str.replace('-', '0')
                         .str.replace(r'\*+', '', regex=True))  # Remove asterisks
            df[col] = pd.to_numeric(temp_series, errors='coerce').fillna(0)
    
    return df

def merge_datasets(families_df: pd.DataFrame, 
                  recipients_df: pd.DataFrame,
                  year: str) -> pd.DataFrame:
    """Merge families and recipients datasets"""
    merged = pd.merge(families_df, recipients_df, on='State', how='outer').copy()
    merged.insert(0, 'Year', year)
    return merged

def format_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Format column names to Title Case"""
    df.columns = [col.title() for col in df.columns]
    return df

def format_final_dataset(df: pd.DataFrame, 
                        output_columns: List[str]) -> pd.DataFrame:
    """Format the final dataset with specified columns"""
    df = df.copy()
    
    for col in output_columns:
        if col not in df.columns:
            df[col] = None
    
    df = df[output_columns].copy()
    
    numeric_cols = df.columns.difference(['Year', 'State'])
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        df[col] = df[col].apply(
            lambda x: "{:,.0f}".format(float(x)) if pd.notnull(x) else "0"
        )
    
    df.columns = [col.title() for col in df.columns]
    return df