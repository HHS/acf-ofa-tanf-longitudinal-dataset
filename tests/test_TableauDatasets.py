import os
import sys
import tempfile
import unittest

import pandas as pd

from data import PCE
from otld.tableau.TableauDatasets import TableauDatasets
from otld.utils.MockData import MockData

TEMP_DIR = tempfile.TemporaryDirectory()
MOCK_DIR = TEMP_DIR.name
for dataset in ["financial", "caseload"]:
    mock_data = MockData(dataset, [2021, 2022, 2023], appended=True)
    mock_data.generate_data()
    mock_data.export(directory=MOCK_DIR, long=True)

FINANCIAL_MOCKED = [
    os.path.join(MOCK_DIR, f) for f in os.listdir(MOCK_DIR) if f.startswith("Financial")
]
FINANCIAL_MOCKED.sort()
FINANCIAL_MOCKED.reverse()
CASELOAD_MOCKED = [
    os.path.join(MOCK_DIR, f) for f in os.listdir(MOCK_DIR) if f.startswith("Caseload")
]
CASELOAD_MOCKED.sort()
CASELOAD_MOCKED.reverse()
assert len(FINANCIAL_MOCKED) == 2, "Incorrect number of financial files."
assert len(CASELOAD_MOCKED) == 2, "Incorrect number of caseload files."

INFLATION = os.path.join(MOCK_DIR, "pce.csv")
with open(INFLATION, "w") as f:
    pd.DataFrame.from_dict(PCE).to_csv(f)
    f.close()


class TestTableauDatasets(unittest.TestCase):
    def setUp(self):
        self.mock_dir = MOCK_DIR
        os.makedirs(os.path.join(self.mock_dir, "tableau"), exist_ok=True)
        self.tableau_dir = os.path.join(self.mock_dir, "tableau")

    def test_validate(self):
        open(os.path.join(self.mock_dir, "caseload.csv"), "w").close()
        arguments = [
            ["tribal", "temp.xlsx", "temp.xlsx", "tempdir/"],
            ["caseload", "temp.xlsx", "temp.xlsx", "tempdir/"],
            ["caseload", CASELOAD_MOCKED[0], "temp.xlsx", "tempdir/"],
            ["caseload", *CASELOAD_MOCKED, "tempdir/"],
            [
                "caseload",
                os.path.join(self.mock_dir, "caseload.csv"),
                CASELOAD_MOCKED[1],
                "tempdir/",
            ],
        ]
        raises = [
            ValueError,
            FileNotFoundError,
            FileNotFoundError,
            FileNotFoundError,
            ValueError,
        ]

        for args, err in zip(arguments, raises):
            sys.argv = ["tanf-tableau"] + args
            with self.assertRaises(err):
                TableauDatasets()

    def test_generate_wide_data(self):
        sys.argv = ["tanf-tableau", "caseload", *CASELOAD_MOCKED, self.tableau_dir]
        tableau_datsets = TableauDatasets()
        tableau_datsets.generate_wide_data()

        self.assertTrue(
            os.path.exists(os.path.join(self.tableau_dir, "CaseloadDataWide.xlsx"))
        )

    def test_generate_long_data(self):
        # Test generating caseload long
        sys.argv = ["tanf-tableau", "caseload", *CASELOAD_MOCKED, self.tableau_dir]
        tableau_datasets = TableauDatasets()
        tableau_datasets.generate_long_data()

        self.assertTrue(
            os.path.exists(os.path.join(self.tableau_dir, "CaseloadDataLong.xlsx"))
        )

        # Test generating financial long
        sys.argv = [
            "tanf-tableau",
            "financial",
            *FINANCIAL_MOCKED,
            self.tableau_dir,
            "-i",
            INFLATION,
        ]
        tableau_datasets = TableauDatasets()
        tableau_datasets.generate_long_data()

        self.assertTrue(
            os.path.exists(os.path.join(self.tableau_dir, "FinancialDataLong.xlsx"))
        )

    def tearDown(self):
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
    # suite = unittest.TestSuite()
    # suite.addTest(TestTableauDatasets("test_validate"))
    # unittest.TextTestRunner().run(suite)
