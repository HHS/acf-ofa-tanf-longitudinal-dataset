import json
import os

import plotly.express as px
from pandas import DataFrame
from plotly.graph_objs._figure import Figure

from otld import combine_appended_files
from otld.paths import input_dir
from otld.utils.string_utils import standardize_line_number

# Line number to field name crosswalk
crosswalk = json.load(open(os.path.join(input_dir, "column_dict_196.json")))
crosswalk = {standardize_line_number(key): value for key, value in crosswalk.items()}
crosswalk.update({"5b": "Assistance: Child Care", "6b": "Non-assistance: Child Care"})


class LongitudinalVisualizations:
    def __init__(
        self,
        df: DataFrame = None,
        state: str | list[str] = None,
        year: int = None,
        column: str | list[str] = None,
    ):
        """Instantiate LongitudinalVisualizations class

        Args:
            df (DataFrame, optional): Data to use for visualizations. Defaults to None.
            state (str | list[str], optional): Single state or list of states. Defaults to None.
            year (int, optional): Year. Defaults to None.
            column (str | list[str], optional): Single line number or list of line numbers. Defaults to None.
        """
        self.df = df
        self.state = state
        self.year = year
        self.column = column

    def cross_state_longitudinal_line_plot(self) -> Figure:
        """Longitudinal line chart across state for select column

        Returns:
            Figure: Line chart
        """
        df = self.df.copy()

        if isinstance(self.state, str):
            df = df[df["STATE"] == self.state]
        elif isinstance(self.state, (list, tuple)):
            df = df[df["STATE"].isin(self.state)]

        df.loc[:, "STATE"] = df.loc[:, "STATE"].map(lambda x: x.title())
        column_name = crosswalk[self.column]

        fig = px.line(
            df,
            "year",
            self.column,
            color="STATE",
            labels={
                "year": "Year",
                self.column: column_name,
                "STATE": "State",
            },
            title=f"Longitudinal Comparison of {column_name}",
        )

        fig.update_layout(xaxis={"dtick": 1})

        # fig.show()

        return fig

    def within_state_within_year_bar_chart(self) -> Figure:
        """Bar chart within state and year of all columns

        Returns:
            Figure: Bar chart
        """
        df = self.df.copy()

        df = df[(df["STATE"] == self.state) & (df["year"] == self.year)]
        if self.column:
            df = df[self.column]
        else:
            df.drop(["STATE", "year"], axis=1, inplace=True)

        df = df.rename(columns=crosswalk)
        df = df.melt()

        fig = px.bar(
            df,
            "variable",
            "value",
            labels={"value": "$Amount", "variable": "Line"},
            title=f"Expenditure Categories for {self.state.title()} in {self.year}",
        )

        return fig

    def within_state_longitudinal_line_plot(self) -> Figure:
        """Longitudinal line chart within state of select columns

        Returns:
            Figure: Line chart
        """
        df = self.df.copy()

        df = df[df["STATE"] == self.state]
        if self.column:
            if isinstance(self.column, str):
                self.column = [self.column]

            self.column.append("year")

            df = df[self.column]
        else:
            df.drop(["STATE"], axis=1, inplace=True)

        df = df.rename(columns=crosswalk)
        df = df.melt(id_vars=["year"])

        fig = px.line(
            df,
            "year",
            "value",
            color="variable",
            labels={"year": "Year", "value": "$Amount", "variable": "Line"},
            title=f"Longitudinal Comparison of Expenditure Categories within {self.state.title()}",
        )

        return fig

    def within_year_within_state_treemap(self) -> Figure:
        """Treemap within state and year of all columns

        Returns:
            Figure: Treemap
        """
        df = self.df.copy()

        df = df.melt(id_vars=["year", "STATE"])
        df = df.fillna(0)
        df = df[(df["year"] == self.year) & (df["STATE"] == self.state)]
        df["variable"] = df.variable.map(crosswalk)
        df = df.sort_values(by=["variable"])

        fig = px.treemap(
            df,
            path=["year", "STATE", "variable"],
            values="value",
            title=f"Expenditure Categories for {self.state.title()} in {self.year}",
        )
        fig.data[0].customdata = df.value.tolist()
        fig.data[0].texttemplate = "%{label}<br>Amount: $%{customdata:,}"

        return fig

    def cross_state_within_year_treemap(self) -> Figure:
        """Treemap across state and within year of select columns

        Returns:
            Figure: Treemap
        """
        df = self.df.copy()

        df = df[df["year"] == self.year]
        df = df[["year", "STATE", self.column]]
        df = df.fillna(0)
        df = df.sort_values(by=["STATE"])
        df["STATE"] = df["STATE"].map(lambda x: x.title())

        fig = px.treemap(
            df,
            path=["year", "STATE"],
            values=self.column,
            title=f"Comparison of {crosswalk[self.column]} in {self.year}",
        )
        fig.data[0].customdata = df[self.column].tolist()
        fig.data[0].texttemplate = "%{label}<br>Amount: $%{customdata:,}"

        return fig


if __name__ == "__main__":
    federal, state = combine_appended_files.main()
    federal_vis = LongitudinalVisualizations(federal, "ALABAMA", 2009, "1")
    federal_vis.column = ["1", "2", "3"]
    federal_vis.cross_state_longitudinal_line_plot().show()
