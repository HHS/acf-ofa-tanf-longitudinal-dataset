from dash import Dash, Input, Output, callback, dcc, html
from LongitudinalVisualizations import LongitudinalVisualizations
from visualization_data import (
    column_checkboxes,
    column_dropdown,
    df_dropdown,
    get_data,
    state_checkboxes,
    state_dropdown,
    year_dropdown,
)

app = Dash(__name__)
visualizer = LongitudinalVisualizations()

app.layout = html.Div(
    [
        dcc.Markdown("# Example Visualizations"),
        dcc.Tabs(
            id="visualizations",
            value="visualizations",
            children=[
                dcc.Tab(
                    label="Cross-state Longitudinal Line Plot",
                    value="cross_state_longitudinal_line_plot",
                ),
                dcc.Tab(
                    label="Within-state, Within-year Bar Chart",
                    value="within_state_within_year_bar_chart",
                ),
                dcc.Tab(
                    label="Within-state Longitudinal Line Plot",
                    value="within_state_longitudinal_line_plot",
                ),
                dcc.Tab(
                    label="Within-year, Within-state Treemap",
                    value="within_year_within_state_treemap",
                ),
                dcc.Tab(
                    label="Cross-state, Within-year Treemap",
                    value="cross_state_within_year_treemap",
                ),
            ],
        ),
        html.Div(id="content-container"),
    ]
)


@callback(Output("content-container", "children"), Input("visualizations", "value"))
def render_tab(tab):
    if tab == "cross_state_longitudinal_line_plot":
        content = html.Div(
            [
                html.Div([df_dropdown, state_checkboxes, column_dropdown]),
                dcc.Graph(id="cross_state_longitudinal_line_plot_plot"),
            ]
        )
    elif tab == "within_state_within_year_bar_chart":
        content = html.Div(
            [
                html.Div([df_dropdown, state_dropdown, year_dropdown]),
                dcc.Graph(id="within_state_within_year_bar_chart_plot"),
            ]
        )
    elif tab == "within_state_longitudinal_line_plot":
        content = html.Div(
            [
                html.Div([df_dropdown, state_dropdown, column_checkboxes]),
                dcc.Graph(id="within_state_longitudinal_line_plot_plot"),
            ]
        )
    elif tab == "within_year_within_state_treemap":
        content = html.Div(
            [
                html.Div([df_dropdown, state_dropdown, year_dropdown]),
                dcc.Graph(id="within_year_within_state_treemap_plot"),
            ]
        )
    elif tab == "cross_state_within_year_treemap":
        content = html.Div(
            [
                html.Div([df_dropdown, year_dropdown, column_dropdown]),
                dcc.Graph(id="cross_state_within_year_treemap_plot"),
            ]
        )
    else:
        content = html.Div()

    return content


@callback(
    Output("plot", "figure"),
    Input("visualizations", "value"),
    Input("content-container", "children"),
)
def render_figure(tab, children):
    selectors = children["props"]["children"][0]["props"]["children"]
    for item in selectors:
        if not isinstance(item, dict):
            continue
        elif not item.get("props"):
            continue

        props = item.get("props")
        ident = props.get("id")
        if ident not in [
            "df-dropdown",
            "state-dropdown",
            "state-checkbox",
            "column-dropdown",
            "column-checkbox",
            "year-dropdown",
        ]:
            continue

        value = props.get("value")
        if ident == "df-dropdown":
            df = value.lower()
            df = get_data(df).copy()
            visualizer.df = df
        elif ident.startswith("state"):
            visualizer.state = value
        elif ident.startswith("column"):
            visualizer.column = value
        elif ident.startswith("year"):
            visualizer.year = value

        # Return the appropriate figure from visualizer
    func = visualizer.__getattribute__(tab)

    return func()


if __name__ == "__main__":
    app.run(debug=True)
