"""Generate column dictionary for revised 196 instructions

Parse revised 196 instructions PDF, extracting line numbers and line
label to create a dictionary which can map column names to line numbers.
"""

import json
import os
import re

import pandas as pd
from pdfminer.high_level import extract_text

from otld.paths import input_dir


def split_line(
    line: str,
    line_re: re.Pattern = re.compile(r"Lines?\s?(.+?\.)\s+(.+?)\.", re.DOTALL),
) -> tuple[str, str]:
    """Split line into line number and name

    Args:
        line (str): The line to be split.
        line_re (re.Pattern, optional): A regex pattern to use to split `line`.
            Defaults to re.compile(r"Lines?\s?(.+?\.)\s+(.+?)\.", re.DOTALL).

    Returns:
        tuple[str, str]: A tuple containing the line_number associated with `line` and
        and the name associated.
    """
    line_number, name = line_re.search(line).groups()
    line_number = line_number.strip().replace(".", "")
    name = name.strip().replace(".", "")
    return line_number, name


def main():
    """Generate column dictionary"""
    # Extract PDF text
    instructions = os.path.join(input_dir, "ACF_196R_Instructions.pdf")
    instructions = extract_text(instructions)
    instructions = instructions.replace("\x0c", "")

    # Extract line numbers and names
    line_re = re.compile(r"(?<=\n)(Lines?\s?\d.+?\.\s+.+?\.)", re.DOTALL)
    lines = line_re.findall(instructions)
    # lines.sort()
    assert len(lines) == 49, "Too few lines found"

    # Create dictionary
    column_dict = [split_line(line) for line in lines]
    column_dict = {key: value for key, value in column_dict if key.strip() != "2 and 3"}

    # Save dictionary
    with open(os.path.join(input_dir, "column_dict_196_r.json"), "w") as file:
        json.dump(column_dict, file, indent=4)

    # Create column_df to export to Excel
    column_df = pd.DataFrame.from_dict(column_dict, orient="index")
    column_df.columns = ["Field Name"]
    column_df.index.name = "Line Number"

    # Update worksheet in instruction Excel file
    instruction_file = os.path.join(input_dir, "Instruction Crosswalk.xlsx")
    sheet_name = "Instructions 196 Revised"
    if os.path.exists(instruction_file):
        writer = pd.ExcelWriter(
            instruction_file, engine="openpyxl", mode="a", if_sheet_exists="replace"
        )
        column_df.to_excel(writer, sheet_name=sheet_name, index=True)
        writer.close()
    else:
        column_df.to_excel(instruction_file, sheet_name=sheet_name, index=True)


if __name__ == "__main__":
    main()
