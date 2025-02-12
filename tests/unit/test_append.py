import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from otld.append.append import TANFAppend
from otld.utils.MockData import MockData


class TestTANFAppend(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mock_dir = self.temp_dir.name
        mock_dir = self.mock_dir
        mock_data = MockData("caseload", 2024)
        mock_data.generate_data()
        mock_data.export(directory=mock_dir)

    def tearDown(self):
        return super().tearDown()

    def test_append(self):
        sys.argv = [
            "tanf-append",
            "caseload",
            os.path.join(self.mock_dir, "CaseloadDataWide.xlsx"),
            "-d",
            self.mock_dir,
        ]

        appender = TANFAppend()
        appender.append = MagicMock()
        appender.append()

        appender.append.assert_called_once()

    def test_get_files(self):
        with open(os.path.join(self.mock_dir, "caseload.txt"), "w") as f:
            f.close()

        with open(os.path.join(self.mock_dir, "financial_2024.txt"), "w") as f:
            f.close()

        sys.argv = [
            "tanf-append",
            "caseload",
            os.path.join(self.mock_dir, "CaseloadDataWide.xlsx"),
            "-d",
            self.mock_dir,
        ]

        appender = TANFAppend()
        files = appender._to_append
        files = [Path(file).name for file in files]
        files.sort()
        correct = [
            "fy2024_ssp_caseload.xlsx",
            "fy2024_tanf_caseload.xlsx",
            "fy2024_tanfssp_caseload.xlsx",
        ]
        correct.sort()
        self.assertEqual(correct, files)

    def test_get_sheets(self):
        # Check that the correct sheets are obtained, financial
        sys.argv = [
            "tanf-append",
            "financial",
            os.path.join(self.mock_dir, "CaseloadDataWide.xlsx"),
            "-d",
            self.mock_dir,
            "-s",
            '{"financial": {"Total": "B. Total Expenditures", "Federal": "C.1 Federal Expenditures", "State": "C.2 State Expenditures"}}',
        ]
        appender = TANFAppend()
        correct = {
            "financial": {
                "Total": "B. Total Expenditures",
                "Federal": "C.1 Federal Expenditures",
                "State": "C.2 State Expenditures",
            }
        }
        self.assertEqual(correct, appender._sheets)

        # Check that the correct sheets are obtained, caseload
        sys.argv = [
            "tanf-append",
            "caseload",
            os.path.join(self.mock_dir, "CaseloadDataWide.xlsx"),
            "-d",
            self.mock_dir,
            "-s",
            """{"caseload": {
                "TANF": {"family": "fycy2024-families", "recipient": "fycy2024-recipients"}, 
                "SSP_MOE": {"family": "Avg Month Num Fam", "recipient": "Avg Mo. Num Recipient"},
                "TANF_SSP": {"family": "fycy2024-families", "recipient": "Avg Mo. Num Recipient"}
            }}""",
        ]
        correct = {
            "caseload": {
                "TANF": {
                    "family": "fycy2024-families",
                    "recipient": "fycy2024-recipients",
                },
                "SSP_MOE": {
                    "family": "Avg Month Num Fam",
                    "recipient": "Avg Mo. Num Recipient",
                },
                "TANF_SSP": {
                    "family": "fycy2024-families",
                    "recipient": "Avg Mo. Num Recipient",
                },
            }
        }
        appender = TANFAppend()
        self.assertEqual(correct, appender._sheets)

        # Confirm error is raised if Total, Federal, or State is missing
        sys.argv = [
            "tanf-append",
            "financial",
            os.path.join(self.mock_dir, "CaseloadDataWide.xlsx"),
            "-d",
            self.mock_dir,
            "-s",
            '{"financial": {"Total": "B. Total Expenditures", "Federal": "C.1 Federal Expenditures"}}',
        ]
        with self.assertRaises(AssertionError):
            TANFAppend()

        # Confirm error is raised if TANF, TANF_SSP, or SSP_MOE is missing
        sys.argv = [
            "tanf-append",
            "caseload",
            os.path.join(self.mock_dir, "CaseloadDataWide.xlsx"),
            "-d",
            self.mock_dir,
            "-s",
            """{"caseload": {
                "TANF": {"family": "fycy2024-families", "recipient": "fycy2024-recipients"}, 
                "TANF_SSP": {"family": "fycy2024-families", "recipient": "Avg Mo. Num Recipient"}
            }}""",
        ]
        with self.assertRaises(AssertionError):
            TANFAppend()

        # Assert error if family or recipient missing from keys
        sys.argv = [
            "tanf-append",
            "caseload",
            os.path.join(self.mock_dir, "CaseloadDataWide.xlsx"),
            "-d",
            self.mock_dir,
            "-s",
            """{"caseload": {
                "TANF": {"family": "fycy2024-families", "recipient": "fycy2024-recipients"}, 
                "SSP_MOE": {"family": "Avg Month Num Fam", "recipient": "Avg Mo. Num Recipient"},
                "TANF_SSP": {"family": "fycy2024-families"}
            }}""",
        ]
        with self.assertRaises(AssertionError):
            TANFAppend()

    def test_tableau(self):
        # Assert tableau parameter is true with the -t option and false otherwise
        sys.argv = [
            "tanf-append",
            "caseload",
            os.path.join(self.mock_dir, "CaseloadDataWide.xlsx"),
            "-d",
            self.mock_dir,
            "-t",
        ]
        self.assertTrue(TANFAppend()._tableau)

        sys.argv = [
            "tanf-append",
            "caseload",
            os.path.join(self.mock_dir, "CaseloadDataWide.xlsx"),
            "-d",
            self.mock_dir,
        ]
        self.assertFalse(TANFAppend()._tableau)

    def test_footnotes(self):
        sys.argv = [
            "tanf-append",
            "caseload",
            os.path.join(self.mock_dir, "CaseloadDataWide.xlsx"),
            "-d",
            self.mock_dir,
            "-f",
            """{
                "TANF": [["Footnote 1"], ["Footnote 2"]],
                "TANF_SSP": [["Footnote 1"], ["Footnote 2"]]
            }""",
        ]
        self.assertEqual(
            {
                "TANF": [["Footnote 1"], ["Footnote 2"]],
                "TANF_SSP": [["Footnote 1"], ["Footnote 2"]],
            },
            TANFAppend()._footnotes,
        )


if __name__ == "__main__":
    unittest.main()
    # suite = unittest.TestSuite()
    # suite.addTest(TestTANFAppend("test_append"))
    # unittest.TextTestRunner().run(suite)
