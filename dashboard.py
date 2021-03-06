import math

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import pickle5 as pickle

from dashfigs import make_fig

#### Initialize app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Sheriff dashboard"

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
        html.H1("Sheriff Dashboard"),
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
    dash.dependencies.Output("bubble_chart", "figure"),
    [dash.dependencies.Input("year_dropdown", "value")],
)
def year_picker(year):
    df2 = df[df[f"has_election_{year}"]]
    fig = make_fig(df2)
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
