"""Command line script to append files."""

import argparse
import os
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
        "-b",
        "--base",
        dest="appended",
        type=str,
        help="Base file containing appended data.",
    )
    parser.add_argument(
        "-a",
        "--append",
        dest="to_append",
        nargs="+",
        type=str,
        help="List of files to append to base file.",
    )
    # Maybe it would be useful to have the option to point to a directory and auto process
    # files according to some rules.

    return parser.parse_args(args)


def main():
    """Instantiate TANFData object and call append method"""
    parser = parse_args(sys.argv[1:])
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
