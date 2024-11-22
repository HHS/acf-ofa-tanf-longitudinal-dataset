import os

import pandas as pd


class LineTracker:
    def __init__(self):
        self.sources = {}

    def export(self, path: str):
        if not os.path.exists(path):
            pd.DataFrame().to_excel(path, sheet_name=list(self.sources.keys())[0])

        excel_writer = pd.ExcelWriter(path, engine="xlsxwriter")

        for year in self.sources:
            df = (
                pd.DataFrame()
                .from_dict(self.sources[year], orient="columns")
                .explode(["BaseColumns", "RenamedColumns"])
            )
            df.to_excel(excel_writer, sheet_name=str(year), index=False)

            # Adapted from https://stackoverflow.com/questions/17326973/is-there-a-way-to-auto-adjust-excel-column-widths-with-pandas-excelwriter
            for column in df:
                column_length = max(df[column].astype(str).map(len).max(), len(column))
                col_idx = df.columns.get_loc(column)
                excel_writer.sheets[str(year)].set_column(
                    col_idx, col_idx, column_length
                )

        excel_writer.close()
