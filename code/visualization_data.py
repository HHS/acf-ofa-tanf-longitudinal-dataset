from dash import dcc
from LongitudinalVisualizations import crosswalk
from pandas import DataFrame

from otld import combine_appended_files


def get_data(level: str) -> DataFrame:
    return globals()[level]


federal, state = combine_appended_files.main()

# List of states
data = {}
data["states"] = {}
data["states"]["federal"] = federal["STATE"].unique().tolist()
data["states"]["state"] = state["STATE"].unique().tolist()

for state_list in data["states"].values():
    state_list.sort()
    state_list.insert(0, state_list.pop(state_list.index("U.S. TOTAL")))

data["states"]["federal"] = [
    {"label": state.title(), "value": state} for state in data["states"]["federal"]
]
data["states"]["state"] = [
    {"label": state.title(), "value": state} for state in data["states"]["state"]
]

# State components
state_checkboxes = dcc.Checklist(
    id={"type": "data", "id": "state-checkbox"},
    options=data["states"]["federal"],
    value=["U.S. TOTAL"],
    inline=True,
)
state_dropdown = dcc.Dropdown(
    id={"type": "data", "id": "state-dropdown"},
    options=data["states"]["federal"],
    value="U.S. TOTAL",
)

# List of columns
data["columns"] = {}
data["columns"]["federal"] = federal.drop(["STATE", "year"], axis=1).columns.tolist()
data["columns"]["state"] = state.drop(["STATE", "year"], axis=1).columns.tolist()

for columns in data["columns"].values():
    columns.sort()

data["columns"]["federal"] = [
    {"label": crosswalk[column], "value": column}
    for column in data["columns"]["federal"]
]
data["columns"]["state"] = [
    {"label": crosswalk[column], "value": column} for column in data["columns"]["state"]
]

# Column components
column_checkboxes = dcc.Checklist(
    id={"type": "data", "id": "column-checkbox"},
    options=data["columns"]["federal"],
    value=[],
    inline=True,
)
column_dropdown = dcc.Dropdown(
    id={"type": "data", "id": "column-dropdown"},
    options=data["columns"]["federal"],
    value="",
)

# Dataset component
df_dropdown = dcc.Dropdown(
    id={"type": "data", "id": "df-dropdown"},
    options=["Federal", "State"],
    value="Federal",
)

# List of years
data["years"] = {}
data["years"]["federal"] = federal["year"].unique().tolist()
data["years"]["state"] = state["year"].unique().tolist()

data["years"]["federal"].sort()
data["years"]["state"].sort()

# Year component
year_dropdown = dcc.Dropdown(
    id={"type": "data", "id": "year-dropdown"},
    options=data["years"]["federal"],
    value=2009,
)
