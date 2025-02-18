import os
import tempfile
import unittest
from tkinter import Tk

import pandas as pd

from data import PCE
from otld.tableau.gui import FileSelect
from otld.utils.MockData import MockData

TEMP_DIR = tempfile.TemporaryDirectory()
MOCK_DIR = TEMP_DIR.name
for dataset in ["financial", "caseload"]:
    mock_data = MockData(dataset, [2021, 2022, 2023], appended=True)
    mock_data.generate_data()
    mock_data.export(directory=MOCK_DIR)

FINANCIAL_MOCKED = [
    os.path.join(MOCK_DIR, f) for f in os.listdir(MOCK_DIR) if f.startswith("Financial")
]
CASELOAD_MOCKED = [
    os.path.join(MOCK_DIR, f) for f in os.listdir(MOCK_DIR) if f.startswith("Caseload")
]
assert len(FINANCIAL_MOCKED) == 1, "Incorrect number of financial files."
assert len(CASELOAD_MOCKED) == 1, "Incorrect number of caseload files."
FINANCIAL_MOCKED = FINANCIAL_MOCKED[0]
CASELOAD_MOCKED = CASELOAD_MOCKED[0]

INFLATION = os.path.join(MOCK_DIR, "pce.csv")
with open(INFLATION, "w") as f:
    pd.DataFrame.from_dict(PCE).to_csv(f)
    f.close()

TABLEAU_DIR = os.path.join(MOCK_DIR, "tableau")
os.mkdir(TABLEAU_DIR)


def assert_appended_exists(path: str, kind: str):
    wide_path = os.path.join(path, f"{kind.title()}DataWide.xlsx")
    long_path = os.path.join(path, f"{kind.title()}DataLong.xlsx")
    try:
        assert os.path.exists(wide_path)
    except Exception:
        return False

    try:
        assert os.path.exists(long_path)
    except Exception:
        return False

    return True


class TestFileSelect(unittest.TestCase):
    def test_gui(self):
        for kind in ["caseload", "financial"]:
            file_select = FileSelect(Tk())
            file_select.kind.set(kind)
            file_select.children["appended_entry"].insert(
                0, eval(f"{kind.upper()}_MOCKED")
            )
            file_select.children["destination_entry"].insert(0, TABLEAU_DIR)
            if kind == "financial":
                file_select.children["inflation_entry"].insert(0, INFLATION)

            try:
                file_select.children["confirm_button"].invoke()
            except Exception as e:
                raise e

            self.assertTrue(assert_appended_exists(TABLEAU_DIR, kind))


if __name__ == "__main__":
    unittest.main()
