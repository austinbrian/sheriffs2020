import math

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import pickle5 as pickle

from dashfigs import make_fig

# df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/solar.csv")
# df = pd.read_pickle("data/merged_data.pkl")
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Sheriff dashboard"
# df = pd.read_pickle("data/merged_data.pkl")

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
    df2["votesize"] = df["total_votes"].apply(lambda x: math.sqrt(x))
    fig = px.scatter(
        df2,
        x="per_dem",
        y="CAP Local/All",
        size="votesize",
        color="per_dem",
        color_continuous_scale=px.colors.sequential.RdBu,
        hover_name="Electoral District",
        hover_data={
            "State": True,
            "per_dem": ":.2%",
            "CAP Local/All": ":0.2f",
            "votesize": False,
            "total_votes": ":,f",
            "Official Name": True,
            "Party Roll Up": True,
        },
        labels={"per_dem": "Dem %", "total_votes": "2020 Total Votes"},
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
