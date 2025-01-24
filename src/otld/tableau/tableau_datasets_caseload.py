import os

from openpyxl.styles.numbers import FORMAT_NUMBER_COMMA_SEPARATED1

from otld.paths import out_dir, tableau_dir
from otld.utils import excel_to_dict, export_workbook, wide_with_index


def generate_wide_data():
    frames = excel_to_dict(os.path.join(out_dir, "CaseloadDataWideClean.xlsx"))
    export_workbook(
        wide_with_index(frames, "CaseloadData"),
        os.path.join(tableau_dir, "data", "CaseloadDataWide.xlsx"),
        format_options={
            "skip_cols": 3,
            "number_format": FORMAT_NUMBER_COMMA_SEPARATED1,
        },
    )


def generate_long_data():
    pass


def main():
    generate_wide_data()


if __name__ == "__main__":
    main()
