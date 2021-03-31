import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import pickle5 as pickle
from dash.dependencies import Input, Output, State

from dashfigs import (
    make_bubble_chart_fig,
    make_table_columns,
    set_table_style_cell_conditional,
    yaxis_cols,
)
from combine import create_combined_metrics

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
        html.H1("Sheriffs For Trusting Communities Election Dashboard"),
        html.Div(
            children=[
                html.P(
                    "Select geography and election year below",
                    style={"font-weight": "bold", "font-size": 16},
                ),
                dcc.Dropdown(
                    id="state_dropdown",
                    options=[{"label": i, "value": i} for i in df.State.unique()],
                    value="Nationwide",
                    placeholder="Nationwide",
                    multi=True,
                    style=dict(width="400px"),
                ),
                dcc.RadioItems(
                    id="year_dropdown",
                    options=[{"label": i, "value": i} for i in ["2021", "2022"]],
                    value="2022",
                    labelStyle={"display": "inline-block"},
                    style={
                        "padding": "10px 20px",
                        "max-width": "120px",
                        "display": "flex",
                        "justify-content": "space-between",
                    },
                ),
                html.P(
                    children=f"This selection has {len(df):,} counties.",
                    id="geography-counter",
                    style={"font-style": "italic", "font-size": 14},
                ),
                html.P("Select y-axis", style={"font-weight": "bold", "font-size": 16}),
                dcc.RadioItems(
                    id="mult_or_single_yaxis",
                    options=[
                        {"label": l, "value": v}
                        for l, v in zip(
                            ["Single Y-Axis", "Multiple Y-Axes"],
                            ["single", "multiple"],
                        )
                    ],
                    value="single",
                    labelStyle={
                        "display": "inline-block",
                        "font-style": "bold",
                    },
                    style={
                        "padding": "10px 20px",
                        "max-width": "300px",
                        "display": "flex",
                        "justify-content": "space-between",
                    },
                ),
                html.P(
                    id="explain-mult",
                    children="",
                    style={
                        "font-style": "italic",
                        "font-size": 12,
                        "max-width": "600px",
                    },
                ),
                dcc.Dropdown(
                    id="yaxis-column",
                    options=yaxis_cols(),
                    value="CAP Local/All",
                    multi=True,
                    style=dict(width="600px"),
                ),
                dcc.Graph(
                    id="bubble_chart",
                    figure=make_bubble_chart_fig(df, "2022", "CAP Local/All"),
                ),
                html.P(
                    "The table below can be filtered using the filter row, and some columns can be toggled on or off.",
                    style={"font-style": "italic"},
                ),
                dash_table.DataTable(
                    id="table",
                    columns=make_table_columns(df),
                    data=df.to_dict("records"),
                    sort_action="native",
                    filter_action="native",
                    style_cell={"textAlign": "left"},
                    style_as_list_view=True,
                    style_cell_conditional=set_table_style_cell_conditional(),
                ),
                html.Div(
                    id="sources",
                    children=[
                        html.P(
                            "This data is provided by Sheriffs for Trusting Communities © 2021"
                        )
                    ],
                    style={"font-style": "italic"},
                ),
            ]
        ),
    ]
)


@app.callback(Output("yaxis-column", "multi"), [Input("mult_or_single_yaxis", "value")])
def select_multiple_or_single_yaxis(value):
    if value == "single":
        return False
    elif value == "multiple":
        return True


@app.callback(Output("yaxis-column", "value"), [Input("mult_or_single_yaxis", "value")])
def reset_yaxis_col_if_switched(value):
    return "CAP Local/All"


@app.callback(
    Output("explain-mult", "children"), [Input("mult_or_single_yaxis", "value")]
)
def print_explain_mult_value(value):
    if value == "multiple":
        return "If multiple items are selected, the values of the relevant axes are scaled using the number of standard deviations away from the mean each county is for that axis item. Then the scores for each county are added together and set at a minimum of zero."


@app.callback(
    Output("geography-counter", "children"),
    [
        Input("year_dropdown", "value"),
        Input("state_dropdown", "value"),
    ],
)
def count_geography(year, state):
    if state == "Nationwide":
        state = df[df[f"has_election_{year}"]].State.unique()
    else:
        if isinstance(state, list):
            if len(state) > 0:
                state = state
            else:
                state = df[df[f"has_election_{year}"]].State.unique()
        else:
            state = [state]
    df2 = df[(df.State.isin(state)) & (df[f"has_election_{year}"])]
    return f"This selection has {len(df2):,} counties."


@app.callback(
    Output("bubble_chart", "figure"),
    [
        Input("year_dropdown", "value"),
        Input("state_dropdown", "value"),
        Input("yaxis-column", "value"),
    ],
)
def update_bubble_chart(year, state, yaxis):
    if state == "Nationwide":
        state = df[df[f"has_election_{year}"]].State.unique()
    else:
        if isinstance(state, list):
            if len(state) > 0:
                state = state
            else:
                state = df[df[f"has_election_{year}"]].State.unique()
        else:
            state = [state]
    df2 = df[df.State.isin(state)]
    if isinstance(yaxis, list):
        if len(yaxis) == 0:
            fig = make_bubble_chart_fig(df2, year, yaxis)
            fig.update_layout(title="No axis selected")
        elif len(yaxis) == 1:
            fig = make_bubble_chart_fig(df2, year, yaxis)
            fig.update_layout(title=f"{yaxis[0]} vs. Dem 2020 Performance")
        else:
            df3 = create_combined_metrics(df2, *yaxis)
            fig = make_bubble_chart_fig(df3, year, "combined_metric")
            fig.update_layout(
                title=f"{', '.join(yaxis)} Combined vs. Dem 2020 Performance",
                yaxis_title="Combined Metric Score",
            )
    else:
        fig = make_bubble_chart_fig(df2, year, yaxis)
        fig.update_layout(title=f"{yaxis} vs. Dem 2020 Performance")
    return fig


@app.callback(Output("state_dropdown", "options"), [Input("year_dropdown", "value")])
def update_state_dropdown_on_year_select(year):
    opts = df[df[f"has_election_{year}"]].State.unique()
    options = [{"label": opt, "value": opt} for opt in opts]
    return options


@app.callback(Output("state_dropdown", "value"), [Input("state_dropdown", "options")])
def reset_states_to_nationwide_on_year_switch(options):
    return "Nationwide"


@app.callback(
    Output("table", "data"),
    [
        Input("year_dropdown", "value"),
        Input("state_dropdown", "value"),
    ],
)
def update_table(year, state):
    if state == "Nationwide":
        state = df[df[f"has_election_{year}"]].State.unique()
    else:
        if isinstance(state, list):
            if len(state) > 0:
                state = state
            else:
                state = df[df[f"has_election_{year}"]].State.unique()
        else:
            state = [state]
    df2 = df[df[f"has_election_{year}"] & (df.State.isin(state))]
    return df2.to_dict("records")


if __name__ == "__main__":
    app.run_server(debug=True)
