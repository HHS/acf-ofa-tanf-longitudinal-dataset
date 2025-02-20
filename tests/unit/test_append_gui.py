import json
import os
import tempfile
import time
import tkinter as tk
import unittest
from tkinter import Tk

from data import CASELOAD_SHEETS, FINANCIAL_SHEETS
from otld.append import gui
from otld.utils.caseload_utils import CASELOAD_FOOTNOTES_WIDE
from otld.utils.MockData import MockData

if os.name != "nt" and os.getenv("GITHUB_ACTIONS"):
    os.system("Xvfb :1 -screen 0 1600x1200x16  &")
    os.environ["DISPLAY"] = ":1.0"

TEMP_DIR = tempfile.TemporaryDirectory()
MOCK_DIR = TEMP_DIR.name
for directory in ["raw", "appended"]:
    os.mkdir(os.path.join(MOCK_DIR, directory))

for dataset in ["financial", "caseload"]:
    mock_data = MockData(dataset, 2024)
    mock_data.generate_data()
    mock_data.export(directory=os.path.join(MOCK_DIR, "raw"))
    del mock_data
    mock_data = MockData(dataset, list(range(2015, 2024)), appended=True)
    mock_data.generate_data()
    mock_data.export(directory=os.path.join(MOCK_DIR, "appended"))

CASELOAD_SHEETS_PATH = os.path.join(MOCK_DIR, "sheets.json")
with open(CASELOAD_SHEETS_PATH, "w") as f:
    json.dump(CASELOAD_SHEETS, f)
    f.close()

CASELOAD_FOOTNOTES_PATH = os.path.join(MOCK_DIR, "footnotes.json")
with open(CASELOAD_FOOTNOTES_PATH, "w") as f:
    json.dump(CASELOAD_FOOTNOTES_WIDE, f)
    f.close()

CURRENT_DATE = time.strftime("%Y%m%d", time.gmtime())


def assert_appended_exists(path: str, kind: str):
    wide_path = os.path.join(path, f"{kind.title()}DataWide_{CURRENT_DATE}.xlsx")
    long_path = os.path.join(path, f"{kind.title()}DataLong_{CURRENT_DATE}.xlsx")
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
    def test_fs_caseload(self):
        kind = "caseload"
        file_select = gui.FileSelect(Tk())
        file_select.kind.set(kind)
        file_select.children["appended_entry"].insert(
            0,
            os.path.join(MOCK_DIR, "appended", f"{kind.title()}DataWide.xlsx").replace(
                "\\", "/"
            ),
        )
        file_select.children["to_append"].children["to_append_entry"].insert(
            0, os.path.join(MOCK_DIR, "raw").replace("\\", "/")
        )
        file_select.children["sheets_text"].insert(
            tk.END, CASELOAD_SHEETS_PATH.replace("\\", "/")
        )
        file_select.children["footnotes_text"].insert(
            tk.END, CASELOAD_FOOTNOTES_PATH.replace("\\", "/")
        )
        try:
            file_select.children["append_button"].invoke()
        except Exception as e:
            raise e

        # Check that files exist
        self.assertTrue(
            assert_appended_exists(os.path.join(MOCK_DIR, "appended"), kind)
        )

    def test_fs_financial(self):
        kind = "financial"
        file_select = gui.FileSelect(Tk())
        file_select.kind.set(kind)
        file_select.children["appended_entry"].insert(
            0,
            os.path.join(MOCK_DIR, "appended", f"{kind.title()}DataWide.xlsx").replace(
                "\\", "/"
            ),
        )
        file_select.children["to_append"].children["to_append_entry"].insert(
            0, os.path.join(MOCK_DIR, "raw").replace("\\", "/")
        )
        file_select.children["sheets_text"].insert(tk.END, json.dumps(FINANCIAL_SHEETS))

        try:
            file_select.children["append_button"].invoke()
        except Exception as e:
            raise e

        # Check that files exist
        self.assertTrue(
            assert_appended_exists(os.path.join(MOCK_DIR, "appended"), kind)
        )


if __name__ == "__main__":
    unittest.main()
    # suite = unittest.TestSuite()
    # suite.addTest(TestFileSelect("test_fs_caseload"))
    # unittest.TextTestRunner().run(suite)
