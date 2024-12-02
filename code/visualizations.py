from dash import ALL, Dash, Input, Output, callback, dcc, html
from LongitudinalVisualizations import LongitudinalVisualizations
from visualization_data import (
    column_checkboxes,
    column_dropdown,
    data,
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
        dcc.Markdown("# Example Visualizations of TANF Longitudinal Data"),
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
    """Render the dropdown menu and figure div for a given tab

    Args:
        tab (_type_): The tab currently displayed for the user

    Returns:
        dash.html.Div: HTML div with desired content (or no content if no tab is selected)
    """
    if tab == "cross_state_longitudinal_line_plot":
        content = html.Div(
            [
                html.Div(
                    [df_dropdown, state_checkboxes, column_dropdown], id="selector-div"
                ),
                dcc.Graph(id="plot"),
            ]
        )
    elif tab == "within_state_within_year_bar_chart":
        content = html.Div(
            [
                html.Div(
                    [df_dropdown, state_dropdown, year_dropdown], id="selector-div"
                ),
                dcc.Graph(id="plot"),
            ]
        )
    elif tab == "within_state_longitudinal_line_plot":
        content = html.Div(
            [
                html.Div(
                    [df_dropdown, state_dropdown, column_checkboxes], id="selector-div"
                ),
                dcc.Graph(id="plot"),
            ]
        )
    elif tab == "within_year_within_state_treemap":
        content = html.Div(
            [
                html.Div(
                    [df_dropdown, state_dropdown, year_dropdown], id="selector-div"
                ),
                dcc.Graph(id="plot"),
            ]
        )
    elif tab == "cross_state_within_year_treemap":
        content = html.Div(
            [
                html.Div(
                    [df_dropdown, year_dropdown, column_dropdown], id="selector-div"
                ),
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
def update_figure(tab: str, values: list):
    """Update the plot div

    Args:
        tab (str): The user's current tab
        values (list): The values of the dropdown/checkbox widgets

    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure
    """
    # Get the appropriate dataset
    df = values[0].lower()
    df = get_data(df).copy()
    visualizer.df = df

    # Determine which values to update and update them
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
        visualizer.column = None
    elif tab == "cross_state_within_year_treemap":
        visualizer.year = values[1]
        visualizer.column = values[2]

    # Get the function to run based on tab and generate the figure
    func = visualizer.__getattribute__(tab)
    fig = func()

    # Reset data
    visualizer.state = visualizer.year = visualizer.column = None

    return fig


@callback(
    Output("selector-div", "children"),
    Input({"type": "data", "id": "df-dropdown"}, "value"),
    Input("selector-div", "children"),
)
def update_selectors(level: str, children):
    level = level.lower()
    for child in children:
        if not isinstance(child, dict) or not child.get("props"):
            continue
        elif not isinstance(child["props"]["id"], dict):
            continue

        ident = child["props"]["id"]["id"]
        if ident == "df-dropdown":
            continue
        elif ident.startswith("state"):
            child["props"]["options"] = data["states"][level]
        elif ident.startswith("column"):
            child["props"]["options"] = data["columns"][level]
        elif ident.startswith("year"):
            child["props"]["options"] = data["years"][level]

    return children


if __name__ == "__main__":
    app.run(debug=True)
