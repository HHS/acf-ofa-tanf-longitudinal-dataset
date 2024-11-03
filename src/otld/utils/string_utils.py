__all__ = ["standardize_name"]

import re


def standardize_name(directory: str) -> str:
    directory = re.sub(r"\s|-", "_", directory)
    directory = re.sub(r"_{1,}", "_", directory)
    directory = directory.lower()
    return directory
