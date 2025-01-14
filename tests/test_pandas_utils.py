import os

import pandas as pd

import otld.utils.pandas_utils as putils
from otld.paths import test_dir


def test_get_header():
    df = pd.read_excel(
        os.path.join(test_dir, "fy2023_ssp_caseload.xlsx"),
        sheet_name="Avg Month Num Fam Oct 22_Sep 23",
        header=None,
    )

    # Test returning header row
    header = putils.get_header(df, 0, "^State$", idx=True)
    assert header == 5

    # Test updating df with appropriate header
    df = putils.get_header(df)

    columns = df.columns.tolist()
    columns = [col.replace("\n", "").replace(" ", "") for col in columns]
    columns.sort()
    assert columns == [
        "NoParentFamilies",
        "OneParentFamilies",
        "State",
        "TotalFamilies",
        "TwoParentFamilies",
    ]


if __name__ == "__main__":
    test_get_header()
