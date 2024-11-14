from dash import dcc
from LongitudinalVisualizations import crosswalk
from pandas import DataFrame

from otld import combine_appended_files


def get_data(level: str) -> DataFrame:
    return globals()[level]


federal, state = combine_appended_files.main()

# List of states
states = federal["STATE"].tolist() + state["STATE"].tolist()
states = list(set(states))
states.sort()
states = [{"label": state.title(), "value": state} for state in states]

# State components
state_checkboxes = dcc.Checklist(
    id={"type": "data", "id": "state-checkbox"},
    options=states,
    value=["U.S. TOTAL"],
)
state_dropdown = dcc.Dropdown(
    id={"type": "data", "id": "state-dropdown"}, options=states, value="U.S. TOTAL"
)

# List of columns
columns = (
    federal.drop(["STATE", "year"], axis=1).columns.tolist()
    + state.drop(["STATE", "year"], axis=1).columns.tolist()
)
columns = list(set(columns))
columns.sort()
columns = [{"label": crosswalk[column], "value": column} for column in columns]

# Column components
column_checkboxes = dcc.Checklist(
    id={"type": "data", "id": "column-checkbox"}, options=columns, value=["1"]
)
column_dropdown = dcc.Dropdown(
    id={"type": "data", "id": "column-dropdown"}, options=columns, value="1"
)

# Dataset component
df_dropdown = dcc.Dropdown(
    id={"type": "data", "id": "df-dropdown"},
    options=["Federal", "State"],
    value="Federal",
)

# List of years
years = federal["year"].tolist() + state["year"].tolist()
years = list(set(years))
years.sort()

# Year component
year_dropdown = dcc.Dropdown(
    id={"type": "data", "id": "year-dropdown"}, options=years, value=2009
)
