import datetime
import unittest

import numpy as np
import pandas as pd

import otld.utils.pandas_utils as putils


class TestPandasUtils(unittest.TestCase):
    def test_get_header(self):
        no_concat_dict = {
            0: {
                0: 2023,
                1: "Separate State Programs - Maintenp.nance of Effort (SSP-MOE)",
                2: "AVERAGE MONTHLY NUMBER OF FAMILIES: Oct. 2022 - Sep. 2023",
                3: "Fiscal Year 2023 (October - September)",
                4: datetime.datetime(2023, 12, 27, 0, 0),
                5: "State",
                6: "U.S. Totals",
                7: "Alabama",
                8: "Alaska",
                9: "Arizona",
            },
            1: {
                0: np.nan,
                1: np.nan,
                2: np.nan,
                3: np.nan,
                4: np.nan,
                5: "Total\nFamilies",
                6: 194919.5,
                7: 0,
                8: 0,
                9: 0,
            },
            2: {
                0: np.nan,
                1: np.nan,
                2: np.nan,
                3: np.nan,
                4: np.nan,
                5: "Two\nParent\nFamilies",
                6: 23386.5,
                7: 0,
                8: 0,
                9: 0,
            },
            3: {
                0: np.nan,
                1: np.nan,
                2: np.nan,
                3: np.nan,
                4: np.nan,
                5: "One \nParent \nFamilies",
                6: 170310,
                7: 0,
                8: 0,
                9: 0,
            },
            4: {
                0: np.nan,
                1: np.nan,
                2: np.nan,
                3: np.nan,
                4: np.nan,
                5: "No \nParent \nFamilies",
                6: 1223,
                7: 0,
                8: 0,
                9: 0,
            },
        }
        df = pd.DataFrame.from_dict(no_concat_dict)

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
        concat_dict = {
            0: {0: np.nan, 1: "State", 2: 1},
            1: {0: "Line 1", 1: "Name", 2: 2},
            2: {0: "Line 2", 1: "Name", 2: 3},
        }
        df = pd.DataFrame.from_dict(concat_dict)

        df = putils.get_header(df, concatenate=True)
        columns = df.columns.tolist()
        columns.sort()
        self.assertEqual(columns, ["Line 1 Name", "Line 2 Name", "State"])
        self.assertEqual(df.iloc[0].tolist(), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
