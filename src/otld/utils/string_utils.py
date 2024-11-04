__all__ = ["standardize_name", "standardize_line_number"]

import re


def standardize_name(directory: str) -> str:
    directory = re.sub(r"\s|-", "_", directory)
    directory = re.sub(r"_{1,}", "_", directory)
    directory = directory.lower()
    return directory


def standardize_line_number(line_number: str) -> str:
    return re.sub(r"\W", "", line_number).strip()
