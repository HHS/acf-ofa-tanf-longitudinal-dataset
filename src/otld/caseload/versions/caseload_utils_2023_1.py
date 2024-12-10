import pandas as pd
from datetime import datetime

def detect_header_row(raw_data, keyword="State"):
    """Detect the header row containing the specified keyword."""
    header_row = raw_data.astype(str).apply(
        lambda row: row.str.contains(keyword, na=False).any(), axis=1
    )
    return header_row.idxmax() if header_row.any() else None

def reshape_to_long_format(data, id_vars=["State"], value_name="Value"):
    """Reshape the DataFrame to long format."""
    return data.melt(id_vars=id_vars, var_name="Year", value_name=value_name)

def reformat_year_column(data, column="Year"):
    """Reformat the Year column to 'Month, Year'."""
    def reformat_year(value):
        try:
            return datetime.strptime(value.strip(), "%b-%y").strftime("%B, %Y")
        except ValueError:
            return value  # Keep as-is for "Average Monthly Numbers"
    data[column] = data[column].apply(reformat_year)
    return data

def clean_metadata_rows(data, state_column="State"):
    """Remove rows with metadata or notes."""
    unwanted_keywords = ["Notes", "Fiscal year average", "data inapplicable"]
    mask = ~data[state_column].str.contains("|".join(unwanted_keywords), na=False, case=False)
    return data[mask]

def format_numeric_values(data, value_column="Value"):
    """Format numeric values with commas for thousands separators."""
    data[value_column] = data[value_column].apply(
        lambda x: "{:,.0f}".format(x) if pd.notnull(x) and isinstance(x, (int, float)) else x
    )
    return data
