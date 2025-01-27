import os
import tempfile
import time
import unittest

import pandas as pd

from otld.append.TANFData import TANFData
from otld.paths import test_dir
from otld.utils.MockData import MockData


class TestTANFData(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mock_dir = self.temp_dir.name

    def test_properties(self):
        mock_dir = self.mock_dir
        mock_data = MockData("caseload", 2024)
        mock_data.generate_data()
        mock_data.export(dir=mock_dir)
        mocked_data = [os.path.join(mock_dir, f) for f in os.listdir(mock_dir)]

        tanf_data = TANFData(
            "caseload",
            os.path.join(test_dir, "CaseloadDataWide.xlsx"),
            mocked_data,
        )

        with self.assertRaises(AttributeError):
            tanf_data.appended = 1

        with self.assertRaises(AttributeError):
            tanf_data.to_append = 1

        with self.assertRaises(AttributeError):
            tanf_data.type = 1

        with self.assertRaises(AttributeError):
            tanf_data.sheet_dict = 1

        tanf_data.close_excel_files()

    def test_append_caseload(self):
        mock_dir = self.mock_dir
        mock_data = MockData("caseload", 2024)
        mock_data.generate_data()
        mock_data.export(dir=mock_dir)
        mocked_data = [os.path.join(mock_dir, f) for f in os.listdir(mock_dir)]

        tanf_data = TANFData(
            "caseload",
            os.path.join(test_dir, "CaseloadDataWide.xlsx"),
            mocked_data,
        )
        tanf_data.append()

        current_date = time.strftime("%Y%m%d", time.gmtime())
        wide_path = os.path.join(test_dir, f"CaseloadDataWide_{current_date}.xlsx")
        long_path = os.path.join(test_dir, f"CaseloadDataLong_{current_date}.xlsx")
        self.assertTrue(os.path.exists(wide_path))
        self.assertTrue(os.path.exists(long_path))

        os.remove(wide_path)
        os.remove(long_path)

        tanf_data.close_excel_files()

    def test_append_expenditure(self):
        mock_dir = self.mock_dir
        mock_data = MockData("financial", 2024)
        mock_data.generate_data()
        mock_data.export(dir=mock_dir)
        mocked_data = [os.path.join(mock_dir, f) for f in os.listdir(mock_dir)]
        assert len(mocked_data) == 1
        mocked_data = mocked_data[0]

        tanf_data = TANFData(
            "financial", os.path.join(test_dir, "FinancialDataWide.xlsx"), mocked_data
        )
        tanf_data.append()

        current_date = time.strftime("%Y%m%d", time.gmtime())
        wide_path = os.path.join(test_dir, f"FinancialDataWide_{current_date}.xlsx")
        long_path = os.path.join(test_dir, f"FinancialDataLong_{current_date}.xlsx")
        self.assertTrue(os.path.exists(wide_path))
        self.assertTrue(os.path.exists(long_path))

        os.remove(wide_path)
        os.remove(long_path)

        tanf_data.close_excel_files()

    def test_get_header_wrapper(self):
        tanf_data = TANFData(
            "financial",
            os.path.join(test_dir, "FinancialDataWide.xlsx"),
            os.path.join(test_dir, "fy2023_ssp_caseload.xlsx"),
        )
        df = pd.read_excel(
            os.path.join(test_dir, "test_get_header.xlsx"),
            sheet_name="test_get_header_wrapper_1",
            header=None,
        )
        columns = tanf_data.get_header_wrapper(df).columns.tolist()
        columns.sort()
        self.assertEqual(columns, ["Line 1 Name", "Line 2 Name", "State"])

        df = pd.read_excel(
            os.path.join(test_dir, "test_get_header.xlsx"),
            sheet_name="test_get_header_wrapper_2",
            header=None,
        )
        columns = tanf_data.get_header_wrapper(df).columns.tolist()
        columns.sort()
        self.assertEqual(columns, ["Line 1 Name", "Line 2 Name", "State"])

    def tearDown(self):
        return super().tearDown()


if __name__ == "__main__":
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestTANFData("test_get_header_wrapper"))
    unittest.TextTestRunner().run(suite)
