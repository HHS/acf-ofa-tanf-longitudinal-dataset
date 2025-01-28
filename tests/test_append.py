import os
import sys
import tempfile
import unittest

import otld.append.append as append
from otld.paths import test_dir
from otld.utils.MockData import MockData


class TestAppend(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mock_dir = self.temp_dir.name
        mock_dir = self.mock_dir
        mock_data = MockData("caseload", 2024)
        mock_data.generate_data()
        mock_data.export(dir=mock_dir)

    def tearDown(self):
        return super().tearDown()

    # def test_main(self):
    #     sys.argv = [
    #         "tanf-append",
    #         "caseload",
    #         "-b",
    #         os.path.join(scrap_dir, "CaseloadDataWide.xlsx"),
    #         "-a",
    #         os.path.join(scrap_dir, "fy2024_ssp_caseload.xlsx"),
    #         os.path.join(scrap_dir, "fy2024_tanf_caseload.xlsx"),
    #         os.path.join(scrap_dir, "fy2024_tanssp_caseload.xlsx"),
    #     ]

    #     append.main()

    def test_get_files(self):
        with open(os.path.join(self.mock_dir, "caseload.txt"), "w") as f:
            f.close()

        with open(os.path.join(self.mock_dir, "financial_2024.txt"), "w") as f:
            f.close()

        sys.argv = [
            "tanf-append",
            "caseload",
            os.path.join(test_dir, "CaseloadDataWide.xlsx"),
            "-d",
            self.mock_dir,
        ]

        parser = append.parse_args(sys.argv[1:])
        files = append.get_files(parser.directory)
        files = [file.split("\\")[-1] for file in files]
        files.sort()
        correct = [
            "fy2024_ssp_caseload.xlsx",
            "fy2024_tanf_caseload.xlsx",
            "fy2024_tanfssp_caseload.xlsx",
        ]
        correct.sort()
        self.assertEqual(correct, files)


if __name__ == "__main__":
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestAppend("test_get_files"))
    unittest.TextTestRunner().run(suite)
