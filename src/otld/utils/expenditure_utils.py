"""Common pandas utilities"""

__all__ = ["reindex_state_year"]


import pandas as pd


def reindex_state_year(
    df: pd.DataFrame, names: list[str] = ["STATE", "year"]
) -> pd.DataFrame:
    """Update the index of the data frame

    Args:
        df (pd.DataFrame): Data frame to update index of.

    Returns:
        pd.DataFrame: Data frame with updated index.
    """
    # Convert index to list
    index_list = df.index.to_list()

    new_index = []
    position = {}

    # Find where year and state are in index
    for i, name in enumerate(df.index.names):
        if name.lower().find("year") > -1:
            year_pos = i

        if name.lower().find("state") > -1:
            state_pos = i

    # Where in the list to move the U.S. Total index
    for i, index in enumerate(index_list):
        if index[state_pos].lower() == "alabama":
            position[index[year_pos]] = i
        elif index[state_pos].lower() == "u.s. total":
            new_index.insert(position[index[year_pos]], index)
            continue

        new_index.append(index)

    # Reindex
    new_index = pd.MultiIndex.from_tuples(new_index, names=names)
    assert len(new_index) == df.shape[0]
    df = df.reindex(new_index)

    return df
