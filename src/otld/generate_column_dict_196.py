import json
import os
import re
from io import StringIO

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

from otld.paths import input_dir


def split_line(
    line: str,
    line_re: re.Pattern = re.compile(r"Lines?\s?(.+?\.)\s+(.+?)$", re.DOTALL),
):
    """
    Split line into line number and name
    """
    line = re.sub(r"<.+?>", "", line)
    line = line_re.search(line)
    if not line:
        return None, None

    line_number, name = line.groups()
    line_number = line_number.strip().replace(".", "")
    name = name.strip().replace(".", "")
    return line_number, name


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
