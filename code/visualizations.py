from dash import ALL, Dash, Input, Output, callback, dcc, html
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
                dcc.Graph(id="plot"),
            ]
        )
    elif tab == "within_state_within_year_bar_chart":
        content = html.Div(
            [
                html.Div([df_dropdown, state_dropdown, year_dropdown]),
                dcc.Graph(id="plot"),
            ]
        )
    elif tab == "within_state_longitudinal_line_plot":
        content = html.Div(
            [
                html.Div([df_dropdown, state_dropdown, column_checkboxes]),
                dcc.Graph(id="plot"),
            ]
        )
    elif tab == "within_year_within_state_treemap":
        content = html.Div(
            [
                html.Div([df_dropdown, state_dropdown, year_dropdown]),
                dcc.Graph(id="plot"),
            ]
        )
    elif tab == "cross_state_within_year_treemap":
        content = html.Div(
            [
                html.Div([df_dropdown, year_dropdown, column_dropdown]),
                dcc.Graph(id="plot"),
            ]
        )
    else:
        content = html.Div()

    return content


@callback(
    Output("plot", "figure"),
    Input("visualizations", "value"),
    Input({"type": "data", "id": ALL}, "value"),
)
def update_figure(tab, values):
    df = values[0].lower()
    df = get_data(df).copy()
    visualizer.df = df
    if tab in [
        "cross_state_longitudinal_line_plot",
        "within_state_longitudinal_line_plot",
    ]:
        visualizer.state = values[1]
        visualizer.column = values[2]
    elif tab in [
        "within_state_within_year_bar_chart",
        "within_year_within_state_treemap",
    ]:
        visualizer.state = values[1]
        visualizer.year = values[2]
    elif tab == "cross_state_within_year_treemap":
        visualizer.year = values[1]
        visualizer.column = values[2]
    func = visualizer.__getattribute__(tab)

    return func()


if __name__ == "__main__":
    app.run(debug=True)
