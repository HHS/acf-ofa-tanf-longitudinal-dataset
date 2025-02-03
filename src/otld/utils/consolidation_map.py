import json
import os

import pandas as pd

from otld.paths import input_dir


def update_consolidation_map(row: pd.Series, map: dict):
    """Add a new entry to the consolidation map

    Args:
        row (pd.Series): A row defining consolidation instructions
        map (dict): The map to store consolidation information

    Raises:
        ValueError: If consolidation instructions are not int or string
    """
    instructions = row["instructions"]
    name = row["name"]
    if isinstance(instructions, int):
        map.update({str(instructions): name})
    elif isinstance(instructions, str):
        instructions = instructions.split(",")
        map.update({i.strip(): name for i in instructions})
    else:
        raise ValueError("Object is not int or str.")


def gen_consolidation_map():
    instructions = pd.ExcelFile(os.path.join(input_dir, "Instruction Crosswalk.xlsx"))
    consolidations = pd.read_excel(instructions, sheet_name="consolidated_categories")
    consolidation_map = {}
    consolidations.apply(
        lambda row: update_consolidation_map(row, consolidation_map), axis=1
    )

    # Adapted from https://stackoverflow.com/questions/620367/how-to-jump-to-a-particular-line-in-a-huge-text-file
    handle = open(__file__, "rb+")
    line_offset = []
    offset = 0
    for line in handle:
        line_offset.append(offset)
        offset += len(line)

    handle.seek(0)

    handle.seek(line_offset[55])
    handle.write(b"CONSOLIDATION_MAP = ")
    handle.write(json.dumps(consolidation_map, indent=4).encode())
    handle.write(b"\n\n")
    handle.write(b'if __name__ == "__main__":\n')
    handle.write(b"\tgen_consolidation_map()")


CONSOLIDATION_MAP = {
    "6": "Basic Assistance",
    "9": "Work, Education, & Training Activities",
    "2": "Child Care (Spent or Transferred)",
    "11a": "Child Care (Spent or Transferred)",
    "22": "Program Management",
    "13": "Refundable Tax Credits",
    "14": "Refundable Tax Credits",
    "7a": "Child Welfare Services",
    "8a": "Child Welfare Services",
    "20": "Child Welfare Services",
    "11b": "Pre-Kindergarten/Head Start",
    "3": "Transferred to SSBG",
    "18": "Out-of-Wedlock Pregnancy Prevention",
    "15": "Non-Recurrent Short Term Benefits",
    "10": "Work Supports & Supportive Services",
    "12": "Work Supports & Supportive Services",
    "16": "Work Supports & Supportive Services",
    "17": "Services for Children & Youth",
    "21": "Services for Children & Youth",
    "7b": "Authorized Solely Under Prior Law",
    "7c": "Authorized Solely Under Prior Law",
    "8b": "Authorized Solely Under Prior Law",
    "8c": "Authorized Solely Under Prior Law",
    "19": "Fatherhood & Two-Parent Family Programs",
    "23": "Other",
}

if __name__ == "__main__":
    gen_consolidation_map()
