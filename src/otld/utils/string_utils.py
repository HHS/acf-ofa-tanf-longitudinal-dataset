__all__ = ["standardize_file_name", "standardize_line_number"]

import re


def standardize_file_name(file: str) -> str:
    """Standardize file names

    Args:
        file (str): The name of a file

    Returns:
        str: File name with spaces and dashes replaced with '_'
    """
    file = re.sub(r"\s|-", "_", file)
    file = re.sub(r"_{1,}", "_", file)
    file = file.lower()
    return file


def standardize_line_number(line_number: str) -> str:
    """Standardize line number

    Args:
        line_number (str): 196 or 196_r line number

    Returns:
        str: Line number with all non word characters removed
    """
    return re.sub(r"\W", "", line_number).strip()
