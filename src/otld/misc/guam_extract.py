import os

import pandas as pd

from otld.paths import diagnostics_dir, out_dir
from otld.utils import excel_to_dict, export_workbook
from otld.utils.caseload_utils import analyze_guam_data


def write_analysis_report(
    ambiguous_patterns: dict, guam_data: pd.DataFrame, output_file: str
):
    """
    Write a focused analysis report including ambiguous value patterns and Guam's data.
    """
    with open(output_file, "w") as f:
        f.write("TANF Caseload Data Analysis Report\n")
        f.write("===============================\n\n")

        # Ambiguous Values Section
        f.write("1. Ambiguous Value Patterns\n")
        f.write("-------------------------\n")
        for col, details in ambiguous_patterns.items():
            if details["ambiguous_values_found"]:
                f.write(f"\nColumn: {col}\n")
                f.write(
                    f"Ambiguous values found: {details['ambiguous_values_found']}\n"
                )
                f.write("\nOccurrences by year:\n")
                for year, values in sorted(details["by_year"].items()):
                    f.write(f"{year}: {values}\n")

        # Guam Section
        f.write("\n\n2. Guam Data Analysis\n")
        f.write("-------------------\n")
        f.write("\nYearly patterns for Guam:\n")

        for col in guam_data.columns:
            if col not in ["State", "Fiscal Year"]:
                f.write(f"\n{col}:\n")
                year_values = guam_data.groupby("Fiscal Year")[col].first()
                for year, value in year_values.items():
                    f.write(f"{year}: {value}\n")


def main():
    guam_analysis = excel_to_dict(os.path.join(out_dir, "CaseloadDataWide.xlsx"))
    for frame in guam_analysis:
        guam_analysis[frame] = analyze_guam_data(guam_analysis[frame]).set_index(
            ["State", "FiscalYear"]
        )

    export_workbook(
        guam_analysis, os.path.join("data/appended_data", "GuamCaseload.xlsx")
    )
    export_workbook(guam_analysis, os.path.join(diagnostics_dir, "GuamCaseload.xlsx"))


if __name__ == "__main__":
    main()
