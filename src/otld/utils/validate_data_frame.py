import pandas as pd
from pandas.api.types import is_numeric_dtype

from otld.utils import STATES


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

    # Confirm all states are valid
    if "State" in df.index.names:
        if isinstance(df.index, pd.MultiIndex):
            index = [i for i, name in enumerate(df.index.names) if name == "State"]
            index = index[0]
            invalid_states = [
                i for i, tup in enumerate(df.index) if tup[index] not in STATES
            ]
        else:
            invalid_states = [i for i, state in df.index if state not in STATES]
        invalid_states = df.index[invalid_states].to_list()
    elif "State" in df.columns:
        invalid_states = [state for state in df["State"] if state not in STATES]

    try:
        assert not any(invalid_states), f"Some states are invalid: {invalid_states}"
    except (UnboundLocalError, NameError):
        pass


if __name__ == "__main__":
    import os

    from otld.paths import inter_dir

    federal = pd.read_csv(
        os.path.join(inter_dir, "federal_2010_2014.csv"), index_col=["STATE", "year"]
    )
    validate_data_frame(federal)
