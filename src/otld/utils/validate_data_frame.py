import pandas as pd
from pandas.api.types import is_numeric_dtype


def validate_data_frame(df: pd.DataFrame):
    # Confirm all columns are numeric
    is_numeric = df.dtypes.map(is_numeric_dtype)
    not_numeric = df.columns[~is_numeric]
    assert is_numeric.all(), f"Some columns not numeric: {not_numeric}"

    # Confirm no columns duplicated
    duplicated = df.columns[df.columns.duplicated()]
    assert not df.columns.duplicated().any(), f"Some columns duplicated: {duplicated}"

    # Confirm no indices duplicated
    duplicated = df.index[df.index.duplicated()]
    assert not df.index.duplicated().any(), f"Some indices duplicated: {duplicated}"


if __name__ == "__main__":
    import os

    from otld.paths import inter_dir

    federal = pd.read_csv(
        os.path.join(inter_dir, "federal_2010_2014.csv"), index_col=["STATE", "year"]
    )
    validate_data_frame(federal)
