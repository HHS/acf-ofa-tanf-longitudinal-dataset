__all__ = ["delete_empty_columns", "get_merged_value", "get_column_names"]

import openpyxl


# Appropriated from Gemini code sample
def delete_empty_columns(
    worksheet: openpyxl.worksheet.worksheet.Worksheet,
) -> openpyxl.worksheet.worksheet.Worksheet:
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


def get_merged_value(
    worksheet: openpyxl.worksheet.worksheet.Worksheet, cell: openpyxl.cell.cell.Cell
) -> str:
    merged_cells = list(worksheet.merged_cells)
    for merged_cell in merged_cells:
        if cell.coordinate in merged_cell:
            first_cell = merged_cell.coord.split(":")[0]
            return worksheet[first_cell].value

    return cell.value if cell.value else ""


def get_column_names(worksheet: openpyxl.worksheet.worksheet.Worksheet) -> list[str]:
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
                column + " " + get_merged_value(worksheet, row[j])
                for j, column in enumerate(columns)
            ]
        else:
            columns = [get_merged_value(worksheet, row[j]) for j in range(len(row))]

        if all(columns):
            break

    columns = [column.strip() for column in columns]
    columns = [column for column in columns if column]
    return columns, i
