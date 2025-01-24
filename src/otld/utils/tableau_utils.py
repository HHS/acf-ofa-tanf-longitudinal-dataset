"""Tableau utilities"""

__all__ = ["wide_with_index"]

import pandas as pd

from otld.utils.expenditure_utils import reindex_state_year


def wide_with_index(frames: dict[pd.DataFrame], tab_name: str = "FinancialData"):
    out = pd.DataFrame()
    for name, data in frames.items():
        data = data.copy()
        data.insert(0, "Funding", name)

        if out.empty:
            out = data
        else:
            out = pd.concat([out, data])

    out.set_index(["Funding", "FiscalYear", "State"], inplace=True)
    out.sort_index(
        level=["Funding", "FiscalYear", "State"],
        ascending=[False, False, True],
        inplace=True,
    )
    out = reindex_state_year(out, list(out.index.names))

    return {tab_name: out.reset_index()}
