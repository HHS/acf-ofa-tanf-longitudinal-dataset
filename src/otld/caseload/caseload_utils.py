import pandas as pd
from typing import List, Optional

def process_sheet(file_path: str, sheet_name: str, skiprows: int, 
                 column_names: List[str]) -> Optional[pd.DataFrame]:
    """Read and process a single Excel sheet"""
    try:
        # Determine the correct number of rows to skip based on the sheet name
        if "FYCY" in sheet_name or "Avg" in sheet_name:
            actual_skiprows = 5
        else:
            actual_skiprows = skiprows
        
        # Read the data with predefined column names
        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            skiprows=actual_skiprows,
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
    df.loc[:, 'State'] = df['State'].str.strip().str.replace('"', '')
    
    unwanted_patterns = [
        'U.S. Totals',
        'data inapplicable',
        'Fiscal year average',
        r'\d{4}-\d{2}-\d{2}',
        '^\s*$',
        '^-'
    ]
    
    pattern = '|'.join(unwanted_patterns)
    df = df[~df['State'].str.contains(pattern, regex=True, na=True)].copy()
    
    numeric_cols = df.columns.difference(['State'])
    for col in numeric_cols:
        if df[col].dtype == 'object':
            temp_series = (df[col].astype(str)
                         .str.strip()
                         .str.replace(',', '')
                         .str.replace('"', '')
                         .str.replace('***', '')
                         .str.replace('-', '0'))
            df.loc[:, col] = pd.to_numeric(temp_series, errors='coerce').fillna(0)
    
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