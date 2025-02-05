import os
import tempfile
import time
import unittest

from data import CASELOAD_DATA_WIDE, FINANCIAL_DATA_WIDE, GET_HEADER_DICT
from otld.append.TANFData import TANFData
from otld.utils.MockData import MockData
from otld.utils.pandas_utils import dict_to_excel

TEMP_DIR = tempfile.TemporaryDirectory()
MOCK_DIR = TEMP_DIR.name
for dataset in ["financial", "caseload"]:
    mock_data = MockData(dataset, 2024)
    mock_data.generate_data()
    mock_data.export(directory=MOCK_DIR)

FINANCIAL_MOCKED = [
    os.path.join(MOCK_DIR, f) for f in os.listdir(MOCK_DIR) if f.startswith("tanf")
]
CASELOAD_MOCKED = [
    os.path.join(MOCK_DIR, f) for f in os.listdir(MOCK_DIR) if not f.startswith("tanf")
]
assert len(FINANCIAL_MOCKED) == 1, "Incorrect number of financial files."
assert len(CASELOAD_MOCKED) == 3, "Incorrect number of caseload files."


class TestTANFData(unittest.TestCase):
    def setUp(self):
        self.mock_dir = MOCK_DIR

    def test_properties(self):
        caseload_data_wide_path = os.path.join(self.mock_dir, "CaseloadDataWide.xlsx")
        dict_to_excel(CASELOAD_DATA_WIDE, caseload_data_wide_path)

        tanf_data = TANFData(
            "caseload",
            caseload_data_wide_path,
            CASELOAD_MOCKED,
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
        caseload_data_wide_path = os.path.join(self.mock_dir, "CaseloadDataWide.xlsx")
        dict_to_excel(CASELOAD_DATA_WIDE, caseload_data_wide_path)

        tanf_data = TANFData(
            "caseload",
            caseload_data_wide_path,
            CASELOAD_MOCKED,
        )
        tanf_data.append()

        current_date = time.strftime("%Y%m%d", time.gmtime())
        wide_path = os.path.join(self.mock_dir, f"CaseloadDataWide_{current_date}.xlsx")
        long_path = os.path.join(self.mock_dir, f"CaseloadDataLong_{current_date}.xlsx")
        self.assertTrue(os.path.exists(wide_path))
        self.assertTrue(os.path.exists(long_path))

        os.remove(wide_path)
        os.remove(long_path)

        tanf_data.close_excel_files()

    def test_append_expenditure(self):
        financial_data_wide = os.path.join(self.mock_dir, "FinancialDataWide.xlsx")
        dict_to_excel(FINANCIAL_DATA_WIDE, financial_data_wide)

        tanf_data = TANFData("financial", financial_data_wide, FINANCIAL_MOCKED[0])
        tanf_data.append()

        current_date = time.strftime("%Y%m%d", time.gmtime())
        wide_path = os.path.join(
            self.mock_dir, f"FinancialDataWide_{current_date}.xlsx"
        )
        long_path = os.path.join(
            self.mock_dir, f"FinancialDataLong_{current_date}.xlsx"
        )
        self.assertTrue(os.path.exists(wide_path))
        self.assertTrue(os.path.exists(long_path))

        os.remove(wide_path)
        os.remove(long_path)

        tanf_data.close_excel_files()

    def test_get_header_wrapper(self):
        financial_data_wide = os.path.join(self.mock_dir, "FinancialDataWide.xlsx")
        dict_to_excel(FINANCIAL_DATA_WIDE, financial_data_wide)

        tanf_data = TANFData(
            "financial",
            financial_data_wide,
            FINANCIAL_MOCKED[0],
        )

        for df in GET_HEADER_DICT.values():
            columns = tanf_data.get_header_wrapper(df).columns.tolist()
            columns.sort()
            self.assertEqual(columns, ["Line 1 Name", "Line 2 Name", "State"])

        tanf_data.close_excel_files()

    def test_get_worksheets(self):
        financial_data_wide = os.path.join(self.mock_dir, "FinancialDataWide.xlsx")
        dict_to_excel(FINANCIAL_DATA_WIDE, financial_data_wide)

        caseload_data_wide_path = os.path.join(self.mock_dir, "CaseloadDataWide.xlsx")
        dict_to_excel(CASELOAD_DATA_WIDE, caseload_data_wide_path)

        # Test externally provided sheets, financial
        tanf_data = TANFData(
            "financial",
            financial_data_wide,
            FINANCIAL_MOCKED,
            sheets={"financial": {"Federal": "September 2023"}},
        )
        tanf_data._level = "Federal"
        self.assertEqual("September 2023", tanf_data.get_worksheets()._sheets)

        tanf_data.close_excel_files()

        # Test internally provided sheets, financial
        tanf_data = TANFData(
            "financial",
            financial_data_wide,
            FINANCIAL_MOCKED[0],
        )
        tanf_data._level = "Federal"
        self.assertEqual("C.1 Federal Expenditures", tanf_data.get_worksheets()._sheets)

        tanf_data.close_excel_files()

        # Test externally provided sheets, caseload
        tanf_data = TANFData(
            "caseload",
            caseload_data_wide_path,
            CASELOAD_MOCKED,
            sheets={
                "caseload": {
                    "TANF": {"family": "September 2023", "recipient": "October 2023"}
                }
            },
        )
        tanf_data._level = "TANF"

        self.assertEqual(
            ["September 2023", "October 2023"], tanf_data.get_worksheets()._sheets
        )

        tanf_data.close_excel_files()

        # Test internally discovered sheets, caseload
        tanf_data = TANFData(
            "caseload",
            caseload_data_wide_path,
            CASELOAD_MOCKED,
        )
        tanf_data._level = "SSP_MOE"
        self.assertEqual(
            ["Avg Month Num Fam", "Avg Mo. Num Recipient"],
            tanf_data.get_worksheets()._sheets,
        )

        tanf_data.close_excel_files()

    def tearDown(self):
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
    # suite = unittest.TestSuite()
    # suite.addTest(TestTANFData("test_append_caseload"))
    # unittest.TextTestRunner().run(suite)
