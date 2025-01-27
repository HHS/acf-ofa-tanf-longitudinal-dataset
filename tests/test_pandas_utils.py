import os
import unittest

import pandas as pd

import otld.utils.pandas_utils as putils
from otld.paths import test_dir


class TestPandasUtils(unittest.TestCase):
    def test_get_header(self):
        df = pd.read_excel(
            os.path.join(test_dir, "fy2023_ssp_caseload.xlsx"),
            sheet_name="Avg Month Num Fam Oct 22_Sep 23",
            header=None,
        )

        # Test returning header row
        header = putils.get_header(df, 0, "^State$", idx=True)
        self.assertEqual(header, 5)

        # Test updating df with appropriate header
        df = putils.get_header(df)

        columns = df.columns.tolist()
        columns = [col.replace("\n", "").replace(" ", "") for col in columns]
        columns.sort()
        self.assertEqual(
            columns,
            [
                "NoParentFamilies",
                "OneParentFamilies",
                "State",
                "TotalFamilies",
                "TwoParentFamilies",
            ],
        )

        # Test concatenation
        df = pd.read_excel(
            os.path.join(test_dir, "test_get_header.xlsx"),
            sheet_name="test_get_header",
            header=None,
        )

        df = putils.get_header(df, concatenate=True)
        columns = df.columns.tolist()
        columns.sort()
        self.assertEqual(columns, ["Line 1 Name", "Line 2 Name", "State"])
        self.assertEqual(df.iloc[0].tolist(), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
