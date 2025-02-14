"""Generate column dictionary for 196 instructions

Parse 196 instructions PDF, extracting line numbers and line
label to create a dictionary which can map column names to line numbers.
"""

import json
import os
import re
from io import StringIO

import pandas as pd
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

from otld.paths import input_dir


def split_line(
    line: str,
    line_re: re.Pattern = re.compile(r"Lines?\s?(.+?\.)\s+(.+?)$", re.DOTALL),
) -> tuple[str, str]:
    """Split line into line number and name

    Args:
        line (str): The line to be split.
        line_re (re.Pattern, optional): A regex pattern to use to split `line`.
        Defaults to re.compile(r"Lines?\s?(.+?\.)\s+(.+?)$", re.DOTALL).

    Returns:
        tuple[str, str]: A tuple containing the line_number associated with `line` and
        and the name associated.
    """
    line = re.sub(r"<.+?>", "", line)
    line = line_re.search(line)
    if not line:
        return None, None

    line_number, name = line.groups()
    line_number = line_number.strip().replace(".", "")
    name = name.strip().replace(".", "")
    return line_number, name


def main():
    """Generate column dictionary"""
    # Extract PDF text as HTML (this allows identifying bolded sections)
    instructions = os.path.join(input_dir, "ACF_196_Instructions.pdf")
    output_string = StringIO()
    with open(instructions, "rb") as file:
        extract_text_to_fp(
            file, output_string, laparams=LAParams(), output_type="html", codec=None
        )
    instructions = output_string.getvalue()

    # Extract line numbers and names
    line_re = re.compile(
        r"<span.+? TimesNewRomanPS-BoldMT.+?>(Lines?.+?)(Automatically|Enter|Block)"
    )
    lines = line_re.findall(instructions)
    lines = [line[0] for line in lines]
    assert len(lines) == 34, "Incorrect number of lines found"

    # Create dictionary
    column_dict = [split_line(line) for line in lines]
    column_dict = {
        key: value for key, value in column_dict if key and value and len(key) < 10
    }

    # Save dictionary
    with open(os.path.join(input_dir, "column_dict_196.json"), "w") as file:
        json.dump(column_dict, file, indent=4)

    # Create column_df to export to Excel
    column_df = pd.DataFrame.from_dict(column_dict, orient="index")
    column_df.columns = ["Field Name"]
    column_df.index.name = "Line Number"

    # Update worksheet in instruction Excel file
    instruction_file = os.path.join(input_dir, "Instruction Crosswalk.xlsx")
    sheet_name = "Instructions 196"
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
