"""Command line script to append files."""

import argparse
import json
import os
import re
import sys

from otld.append.TANFData import TANFData


class TANFAppend:
    def __init__(self):
        parser = self.parse_args(sys.argv[1:])
        self._kind = parser.kind
        self._appended = parser.appended
        self._to_append = parser.to_append
        self._directory = parser.directory
        self._sheets = parser.sheets
        self.setup()

    def setup(self):
        if not self._to_append:
            self.get_files()

        if self._sheets:
            self.get_sheets()

        return self

    def parse_args(self, args: list[str]) -> argparse.Namespace:
        """Command line argument parser.

        Args:
            args (list): List of command line arguments
        """
        parser = argparse.ArgumentParser(
            prog="tanf-append", description="Append TANF data"
        )
        parser.add_argument("kind", type=str, help="Type of data to append.")
        parser.add_argument(
            "appended",
            type=str,
            help="Base file containing appended data.",
        )
        to_append_group = parser.add_mutually_exclusive_group(required=True)
        to_append_group.add_argument(
            "-a",
            "--append",
            dest="to_append",
            nargs="+",
            type=str,
            help="List of files to append to base file.",
        )
        to_append_group.add_argument(
            "-d",
            "--dir",
            dest="directory",
            type=str,
            help="Directory in which to find files to append.",
        )
        parser.add_argument(
            "-s",
            "--sheets",
            dest="sheets",
            type=str,
            help="List of sheets to extract from files to append. Should be a JSON formatted string.",
        )

        return parser.parse_args(args)

    def get_files(self):
        self._to_append = []
        files = os.scandir(self._directory)
        for file in files:
            if re.search(rf"{self._kind}.*xlsx?$", file.name) and re.search(
                r"\d{4}", file.name
            ):
                self._to_append.append(file.path)

        return self

    def get_sheets(self):
        self._sheets = json.loads(self._sheets)

        if self._kind == "financial":
            levels = ["Federal", "State", "Total"]
            additional_checks = []
        elif self._kind == "caseload":
            levels = ["TANF", "TANF_SSP", "SSP_MOE"]
            additional_checks = [
                "isinstance(self._sheets[self._kind][level], dict)",
                '["family", "recipient"] == list(self._sheets[self._kind][level].keys())',
            ]

        for level in levels:
            assert (
                level in self._sheets[self._kind].keys()
            ), f"{level} missing from sheets."
            for check in additional_checks:
                assert eval(check), f"Check failed: {check}"

        return self

    def append(self):
        """Instantiate TANFData object and call append method"""
        tanf_data = TANFData(self._kind, self._appended, self._to_append, self._sheets)
        tanf_data.append()


def main():
    appender = TANFAppend()
    appender.append()


if __name__ == "__main__":
    from otld.paths import test_dir

    # sys.argv = [
    #     "tanf-append",
    #     "caseload",
    #     os.path.join(test_dir, "CaseloadDataWide.xlsx"),
    #     "-a",
    #     os.path.join(test_dir, "mock", "fy2024_ssp_caseload.xlsx"),
    #     os.path.join(test_dir, "mock", "fy2024_tanf_caseload.xlsx"),
    #     os.path.join(test_dir, "mock", "fy2024_tanfssp_caseload.xlsx"),
    # ]

    sys.argv = [
        "tanf-append",
        "financial",
        os.path.join(test_dir, "FinancialDataWide.xlsx"),
        "-d",
        os.path.join(test_dir, "mock"),
    ]
    TANFAppend()
