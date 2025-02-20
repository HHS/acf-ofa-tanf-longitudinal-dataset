import os
import re
import subprocess

import pandas as pd

from otld.paths import root

DOCS_DIR = os.path.join(root, "documentation")
ROOT = os.path.join(os.path.dirname(__file__), "..")
CSV_DIR = os.path.join(ROOT, "documentation", "csv")
SOURCE_DIR = os.path.join(ROOT, "documentation", "source")


def appendices_to_csv(input: str | os.PathLike, output: str | os.PathLike):
    """Convert excel workbook of appendices to individual csvs

    Args:
        path (str | os.PathLike): Path to Excel Workbook containing appendices
        output (str | os.PathLike): Path to output directory.
    """
    workbook = pd.ExcelFile(input)
    worksheets = workbook.sheet_names

    for sheet in worksheets:
        pd.read_excel(workbook, sheet).to_csv(os.path.join(output, sheet + ".csv"))


def convert_transformation_documentation(
    input: str | os.PathLike, output: str | os.PathLike
):
    """Convert the transformation documentation from docx to rst

    Args:
        input (str | os.PathLike): Path to transformation documentation
        output (str | os.PathLike): Path to output directory
    """

    # Convert to rst
    file = os.path.split(input)[-1].replace("docx", "rst")
    file = os.path.join(output, file)
    subprocess.run(["pandoc", "-o", file, input])

    # Read rst and find where to begin overwriting
    text = open(file, "r", encoding="utf-8").read()

    # Find appendix tables
    appendices = re.findall(r"Appendix [A-Z]:.*", text)
    appendices = [
        (appendix, re.search(appendix, text).span()) for appendix in appendices
    ]
    appendices.reverse()  # Reverse the list to work backward from furthest appendix
    stop = text.find(".. [1]")  # Find the place to stop replacing text

    # Replace appendix text with csv-table directives
    for appendix in appendices:
        title = appendix[0]
        span = appendix[1]
        letter = re.search(r"([A-Z]):", title).group(1)

        new_text = f"{title}\n{"~"*len(title)}\n\n.. csv-table::\n\t:file: ../csv/Appendix {letter}.csv\n\t:header-rows: 1\n\n"

        text_span = text[span[0] : stop]
        text = text.replace(text_span, new_text)

        stop = span[0]

    # Replace title
    text = text.replace(
        "Creating a Longitudinal TANF Funding & Expenditures Dataset: Transformation Description",
        "Transformations",
    )

    # Write text to rst
    with open(file, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    appendices_to_csv(os.path.join(DOCS_DIR, "Appendices.xlsx"), CSV_DIR)
    convert_transformation_documentation(
        os.path.join(DOCS_DIR, "TransformationDocumentation.docx"), SOURCE_DIR
    )


if __name__ == "__main__":
    main()
