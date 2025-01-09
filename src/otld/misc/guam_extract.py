import os
import re
from typing import List, Optional

import pandas as pd

from otld.utils.caseload_utils import (
    analyze_ambiguous_values,
    analyze_guam_data,
    clean_dataset,
    fix_fiscal_year_column,
    format_final_dataset,
    merge_datasets,
    process_1997_1998_1999_data,
    process_sheet,
)


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
    if any(not df.empty for df in master_wide.values()):
        # Generate focused analysis
        analysis_results = {}
        guam_analysis = {}

        for division_name, df in master_wide.items():
            # Analyze ambiguous values
            analysis_results[division_name] = analyze_ambiguous_values(df)

            # Extract Guam's data
            guam_analysis[division_name] = analyze_guam_data(df)

        # Write focused analysis report
        with open("src/otld/caseload/appended_data/analysis_report.txt", "w") as f:
            f.write("TANF Caseload Data Analysis Report\n")
            f.write("===============================\n\n")

            for division_name in master_wide.keys():
                f.write(f"\n{division_name} Division\n")
                f.write("-" * len(f"{division_name} Division") + "\n")

                # Write ambiguous value patterns
                patterns = analysis_results[division_name]
                f.write("\nAmbiguous Value Patterns:\n")
                for col, details in patterns.items():
                    if details["ambiguous_values_found"]:
                        f.write(f"\n{col}:\n")
                        f.write(f"Values found: {details['ambiguous_values_found']}\n")
                        for year, values in sorted(details["by_year"].items()):
                            if values:
                                f.write(f"{year}: {values}\n")

                # Write Guam analysis
                guam_data = guam_analysis[division_name]
                f.write("\nGuam Data Analysis:\n")
                for col in guam_data.columns:
                    if col not in ["State", "Fiscal Year"]:
                        f.write(f"\n{col}:\n")
                        year_values = guam_data.groupby("Fiscal Year")[col].first()
                        for year, value in year_values.items():
                            f.write(f"{year}: {value}\n")

                f.write("\n" + "=" * 50 + "\n")

        # Save Guam data separately
        with pd.ExcelWriter(
            "src/otld/caseload/appended_data/GuamCaseload.xlsx"
        ) as writer:
            for division_name, guam_df in guam_analysis.items():
                guam_df.to_excel(writer, sheet_name=division_name, index=False)
