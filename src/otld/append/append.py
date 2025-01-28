"""Command line script to append files."""

import argparse
import json
import os
import re
import sys

from otld.append.TANFData import TANFData


def parse_args(args: list[str]) -> argparse.Namespace:
    """Command line argument parser.

    Args:
        args (list): List of command line arguments
    """
    parser = argparse.ArgumentParser(prog="tanf-append", description="Append TANF data")
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
        nargs="+",
        type=str,
        help="List of sheets to extract from files to append. Should be a JSON formatted string.",
    )

    return parser.parse_args(args)


def get_files(directory: str):
    to_append = []
    files = os.scandir(directory)
    for file in files:
        if re.search(r"(caseload|financial).*xlsx?$", file.name) and re.search(
            r"\d{4}", file.name
        ):
            to_append.append(file.path)

    return to_append


def main():
    """Instantiate TANFData object and call append method"""
    parser = parse_args(sys.argv[1:])
    if parser.directory:
        parser.to_append = get_files(parser.directory)
    if parser.sheets:
        sheets = json.loads(parser.sheets)
    tanf_data = TANFData(parser.kind, parser.appended, parser.to_append)
    tanf_data.append()


if __name__ == "__main__":
    from otld.paths import scrap_dir

    sys.argv = [
        "tanf-append",
        "caseload",
        "-b",
        os.path.join(scrap_dir, "CaseloadDataWide.xlsx"),
        "-a",
        os.path.join(scrap_dir, "fy2024_ssp_caseload.xlsx"),
        os.path.join(scrap_dir, "fy2024_tanf_caseload.xlsx"),
        os.path.join(scrap_dir, "fy2024_tanssp_caseload.xlsx"),
    ]
    main()
