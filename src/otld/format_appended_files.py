"""Format appended files

This module formats appended TANF financial data.
"""

import os

import openpyxl
import pandas as pd
from openpyxl.styles.alignment import Alignment
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

from otld import append_1997_2009


def format_pd_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Format pandas data frame columns.

    Apply transformations to column values.

    Args:
        df (pd.DataFrame): Data frame to format.

    Returns:
        pd.DataFrame: Formatted data frame.
    """
    df = df.map(lambda x: f"{x:,.0f}")

    return df


def add_table(ws: Worksheet, displayName: str, ref: str):
    """Add an Excel table to a worksheet.

    Args:
        ws (Worksheet): Worksheet to add table to.
        displayName (str): Name of the table.
        ref (str): Range of cells to convert to a table.
    """
    tab = Table(displayName=displayName, ref=ref)

    style = TableStyleInfo(
        name="TableStyleMedium9", showRowStripes=True, showColumnStripes=True
    )
    tab.tableStyleInfo = style

    ws.add_table(tab)


def format_openpyxl_worksheet(ws: Worksheet):
    """Format openpyxl worksheet.

    Args:
        ws (Worksheet): Worksheet to format.
    """
    # Adjust columns
    for column in range(ws.max_column):
        column += 1
        column_letter = get_column_letter(column)
        column = ws.column_dimensions[column_letter]
        # Adjust width
        column.width = 25.0

        # Align right
    for i, row in enumerate(ws.rows):
        if i == 0:
            continue

        for cell in row[2:]:
            cell.alignment = Alignment(horizontal="right")


def main():
    """Entry point for script to format appended files"""

    federal, state = append_1997_2009.main()

    # Load csv into workbook
    # Adapted from https://stackoverflow.com/questions/12976378/openpyxl-convert-csv-to-excel
    wb = openpyxl.Workbook()
    ws = wb.active

    i = 0
    for df in [federal, state]:
        if i == 0:
            sheet = "Federal"
            ws = wb.active
            ws.title = "Federal"
        else:
            sheet = "State"
            wb.create_sheet(sheet)
            ws = wb[sheet]

        i += 1

        df = format_pd_columns(df)
        df = dataframe_to_rows(df.reset_index(), index=False)

        for row in df:
            ws.append(row)

        add_table(ws, sheet, ws.dimensions)
        format_openpyxl_worksheet(ws)

    # Export
    wb.save(os.path.join(scrap_dir, "styling.xlsx"))


if __name__ == "__main__":
    from otld.paths import scrap_dir

    main()
