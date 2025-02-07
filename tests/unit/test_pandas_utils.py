import unittest

import pandas as pd

import otld.utils.pandas_utils as putils
from data import CONCAT_DICT, NO_CONCAT_DICT


class TestPandasUtils(unittest.TestCase):
    def test_get_header(self):
        df = pd.DataFrame.from_dict(NO_CONCAT_DICT)

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

        df = pd.DataFrame.from_dict(CONCAT_DICT)

        df = putils.get_header(df, concatenate=True)
        columns = df.columns.tolist()
        columns.sort()
        self.assertEqual(columns, ["Line 1 Name", "Line 2 Name", "State"])
        self.assertEqual(df.iloc[0].tolist(), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
