import math

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import pickle5 as pickle
from dash.dependencies import Input, Output, State

from dashfigs import make_fig

#### Initialize app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Sheriffs for Trusting Communities"

#### Get data
with open("data/merged_data.pkl", "rb") as fh:
    df = pickle.load(fh)

states_21 = [i for i in df[df.has_election_2021].state_name.unique()]
usecols = [
    "State",
    "Electoral District",
    "county_fips",
    "statecode",
    "Office Name",
    "Official Name",
    "Party Roll Up",
    "per_dem",
    "has_election_2021",
    "has_election_2022",
]

app.layout = html.Div(
    [
        html.H1("Sheriffs on the Bubble"),
        dcc.Dropdown(
            id="year_dropdown",
            options=[{"label": i, "value": i} for i in [2021, 2022]],
            value="2022",
            placeholder="Election Year",
        ),
        dcc.Dropdown(
            id="state_dropdown",
            options=[{"label": i, "value": i} for i in df.State.unique()],
            value="Nationwide",
            placeholder="Nationwide",
        ),
        dcc.Graph(id="bubble_chart", figure=make_fig(df)),
        dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in df[usecols]],
            data=df.to_dict("records"),
            sort_action="native",
            filter_action="native",
        ),
    ]
)


@app.callback(
    Output("bubble_chart", "figure"),
    [Input("year_dropdown", "value"), Input("state_dropdown", "value")],
)
def update_bubble_chart(year, state):
    if state == "Nationwide":
        state = df[df[f"has_election_{year}"]].State.unique()
    else:
        state = [state]
    df2 = df[df[f"has_election_{year}"] & (df.State.isin(state))]
    fig = make_fig(df2)
    return fig


@app.callback(Output("state_dropdown", "options"), [Input("year_dropdown", "value")])
def update_state_dropdown_on_year_select(year):
    opts = df[df[f"has_election_{year}"]].State.unique()
    options = [{"label": opt, "value": opt} for opt in opts]
    # options.append({"label": "Nationwide", "value": "Nationwide"})
    return options


@app.callback(Output("state_dropdown", "value"), [Input("state_dropdown", "options")])
def callback(value):
    return "Nationwide"


if __name__ == "__main__":
    app.run_server(debug=True)
