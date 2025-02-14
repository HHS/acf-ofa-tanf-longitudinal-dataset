import os
import tempfile
import unittest
from unittest import TestCase

import pandas as pd

from otld.utils import openpyxl_utils
from otld.utils.MockData import MockData

TEMP_DIR = tempfile.TemporaryDirectory()
mock_data = MockData("caseload", 2024)
mock_data.generate_data()
mock_data.export(pandas=True)
mock_data.frames = {
    key: pd.read_excel(value).set_index("State")
    for key, value in mock_data.pandas.items()
}


class TestExportWorkbook(TestCase):
    def test_footnotes(self):
        # Define expected footnotes
        expected = [[["One Note"]], [["Multiple"], ["Notes"]], [[]]]

        # Define output path
        output = os.path.join(TEMP_DIR.name, "test_wb.xlsx")

        # Export a workbook with footnotes
        openpyxl_utils.export_workbook(
            mock_data.frames,
            output,
            footnotes={
                key: value
                for key, value in zip(
                    mock_data.frames.keys(),
                    expected,
                )
            },
        )

        # Load the workbook, and confirm that the footnotes are as expected
        footnotes = pd.ExcelFile(output)
        for i, sheet in enumerate(footnotes.sheet_names):
            # Read worksheet and look for note rows
            worksheet = pd.read_excel(footnotes, sheet)
            max_row = worksheet.shape[0]
            notes = expected[i]
            current = max_row - len(notes)

            # Skip if no notes are expected
            if not any(notes):
                continue

            # Confirm notes match
            j = 0
            while current <= max_row - 1:
                assert (
                    worksheet.iloc[current, 0] == notes[j][0]
                ), f"Footnote mismatch {worksheet.iloc[current, 0]}: {notes[j][0]}"
                current += 1
                j += 1

        footnotes.close()


if __name__ == "__main__":
    unittest.main()
