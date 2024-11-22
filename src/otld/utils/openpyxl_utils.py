"""Common openpyxl utilities"""

__all__ = ["delete_empty_columns", "get_merged_value", "get_column_names"]

import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


# Appropriated from Gemini code sample
def delete_empty_columns(
    worksheet: Worksheet,
) -> Worksheet:
    """Delete columns with all NA/empty values

    Args:
        worksheet (Worksheet): Worksheet to delete columns from.

    Returns:
        Worksheet: Worksheet with empty columns removed
    """
    # Iterate over columns in reverse order to avoid index issues when deleting
    for column in range(worksheet.max_column, 0, -1):
        is_empty = True
        for row in worksheet.iter_rows(min_col=column, max_col=column):
            cell = row[0]
            if cell.value is not None:
                is_empty = False
                break

        if is_empty:
            worksheet.delete_cols(column)


def get_merged_value(worksheet: Worksheet, cell: openpyxl.cell.cell.Cell) -> str:
    """Return the value in the first cell of a range of merged cells

    Args:
        worksheet (Worksheet): The worksheet to search in for merged cells.
        cell (openpyxl.cell.cell.Cell): The cell to check for in the merged cells.

    Returns:
        str: The value of the first merged cell or the cell's value if it is not in a
        range of merged cells.
    """
    merged_cells = list(worksheet.merged_cells)
    for merged_cell in merged_cells:
        if cell.coordinate in merged_cell:
            first_cell = merged_cell.coord.split(":")[0]
            return worksheet[first_cell].value

    return cell.value if cell.value else ""


def get_column_names(worksheet: Worksheet) -> list[str]:
    """Get the column names of an Excel worksheet

    This function iterates through the rows in an Excel worksheet until all columns
    have a non-empty value and then returns these as candidate column names.

    Args:
        worksheet (Worksheet): An Excel worksheet.

    Returns:
        list[str]: A list of potential column names
    """
    i = 0
    columns = []
    # If not all column names are present, concatenate current row with next
    # row
    for row in worksheet.rows:
        i += 1
        if i == 1:
            continue

        if columns:
            columns = [
                (column + " " + get_merged_value(worksheet, row[j])).strip()
                for j, column in enumerate(columns)
            ]
        else:
            columns = [get_merged_value(worksheet, row[j]) for j in range(len(row))]

        if all(columns):
            break

    columns = [column.strip() for column in columns]
    columns = [column for column in columns if column]
    return columns, i


def set_column_widths(worksheet: Worksheet, column_width: int | list[int]) -> Worksheet:
    """Set the column widths for an Excel worksheet.

    Args:
        worksheet (Worksheet): An openpyxl worksheet.
        column_width (int | list[int]): Integer, or list of integers specifying column
        width(s)

    Returns:
        Worksheet: Updated worksheet
    """
    for index in range(worksheet.max_column):
        width = column_width if isinstance(column_width, int) else column_width[index]
        index += 1
        column_letter = get_column_letter(index)
        dimensions = worksheet.column_dimensions[column_letter]
        # Adjust width
        dimensions.width = width

    return worksheet
