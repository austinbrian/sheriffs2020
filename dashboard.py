import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import pickle5 as pickle
from dash.dependencies import Input, Output, State

from dashfigs import make_bubble_chart_fig, make_table_columns

#### Initialize app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Sheriffs for Trusting Communities"

#### Get data
with open("data/merged_data.pkl", "rb") as fh:
    df = pickle.load(fh)


app.layout = html.Div(
    [
        html.H1("Sheriffs on the Bubble"),
        html.Div(
            children=[
                dcc.Dropdown(
                    id="year_dropdown",
                    options=[{"label": i, "value": i} for i in [2021, 2022]],
                    value="2022",
                    placeholder="Election Year",
                    style=dict(width="200px"),
                ),
                dcc.Dropdown(
                    id="state_dropdown",
                    options=[{"label": i, "value": i} for i in df.State.unique()],
                    value="Nationwide",
                    placeholder="Nationwide",
                    multi=True,
                    style=dict(width="400px"),
                ),
            ]
        ),
        dcc.Graph(id="bubble_chart", figure=make_bubble_chart_fig(df)),
        # TODO: fix styling to change the names of the columns
        dash_table.DataTable(
            id="table",
            columns=make_table_columns(df),
            data=df.to_dict("records"),
            sort_action="native",
            filter_action="native",
            style_cell={"textAlign": "left"},
            style_as_list_view=True,
            style_cell_conditional=[
                {"if": {"column_id": c}, "textAlign": "right"}
                for c in [
                    "per_dem",
                    "CAP Local/All",
                    "Detainers Total",
                    "Deaths_per_thousand_pop",
                    "killings_per_k_arrests",
                ]
            ],
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
        if isinstance(state, list):
            state = state
        else:
            state = [state]
    df2 = df[df[f"has_election_{year}"] & (df.State.isin(state))]
    fig = make_bubble_chart_fig(df2)
    return fig


@app.callback(Output("state_dropdown", "options"), [Input("year_dropdown", "value")])
def update_state_dropdown_on_year_select(year):
    opts = df[df[f"has_election_{year}"]].State.unique()
    options = [{"label": opt, "value": opt} for opt in opts]
    return options


@app.callback(Output("state_dropdown", "value"), [Input("state_dropdown", "options")])
def reset_states_to_nationwide_on_year_switch(value):
    return "Nationwide"


@app.callback(
    Output("table", "data"),
    [Input("year_dropdown", "value"), Input("state_dropdown", "value")],
)
def update_table(year, state):
    if state == "Nationwide":
        state = df[df[f"has_election_{year}"]].State.unique()
    else:
        if isinstance(state, list):
            state = state
        else:
            state = [state]
    df2 = df[df[f"has_election_{year}"] & (df.State.isin(state))]
    return df2.to_dict("records")


if __name__ == "__main__":
    app.run_server(debug=True)
