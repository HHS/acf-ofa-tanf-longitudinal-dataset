"""Generate column dictionary for revised 196 instructions

Parse revised 196 instructions PDF, extracting line numbers and line
label to create a dictionary which can map column names to line numbers.
"""

import json
import os
import re

from pdfminer.high_level import extract_text

from otld.paths import input_dir


def split_line(
    line: str,
    line_re: re.Pattern = re.compile(r"Lines?\s?(.+?\.)\s+(.+?)\.", re.DOTALL),
):
    """
    Split line into line number and name
    """
    line_number, name = line_re.search(line).groups()
    line_number = line_number.strip().replace(".", "")
    name = name.strip().replace(".", "")
    return line_number, name


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
