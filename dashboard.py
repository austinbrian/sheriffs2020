import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import pickle5 as pickle
from dash.dependencies import Input, Output, State

from components.dashfigs import (
    make_bubble_chart_fig,
    make_table_columns,
    set_table_style_cell_conditional,
    yaxis_cols,
    xaxis_cols,
)
from combine import create_combined_metrics
from components import YDiv, XDiv

#### Initialize app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Sheriffs for Trusting Communities"

#### Get data
with open("data/merged_data_sheriffs.pkl", "rb") as fh:
    df = pickle.load(fh)

with open("data/elections_2018/attempt_4.pkl", "rb") as fh:
    e18 = pickle.load(fh).reset_index(drop=True)
    e18["pres"] = e18.FIPS.map(df.set_index("county_fips")["per_dem"].to_dict())
    e18["gov"] = e18.loc[e18[e18.office == "Governor"].index, "Dem%"]
    e18["sen"] = e18.loc[e18[e18.office == "U.S. Senate"].index, "Dem%"]
    e18["ltgov"] = e18.loc[e18[e18.office == "Lieutenant Governor"].index, "Dem%"]
    e18["ag"] = e18.loc[e18[e18.office.str.lower() == "attorney general"].index, "Dem%"]
    egr = (
        e18[["FIPS", "pres", "gov", "sen", "ltgov", "ag"]]
        .groupby("FIPS")[["pres", "gov", "sen", "ltgov", "ag"]]
        .sum()
        .replace(0.0, pd.np.nan)
    )
    df = df.merge(egr, how="left", left_on="county_fips", right_on="FIPS")
    df["pres"] = df["per_dem"].copy()

app.layout = html.Div(
    [
        html.H1("Sheriffs for Trusting Communities Election Dashboard"),
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
                html.Div(
                    [YDiv(), XDiv()],
                    style={"display": "flex", "width": "95%"},
                ),
                dcc.Graph(
                    id="bubble_chart",
                    figure=make_bubble_chart_fig(df, "2022", "CAP Local/All", "pres"),
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
    ],
    style={"padding": "30px", "margin-bottom": "25px"},
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
    Output("explain-x-axis", "children"), [Input("xaxis-checkboxes", "value")]
)
def print_explain_mult_value_xaxis(value):
    if len(value) > 1:
        return "If multiple races are selected, the X-axis shows the average Democratic performance for a county across the selected races."
    else:
        return ""


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
        Input("xaxis-checkboxes", "value"),
    ],
)
def update_bubble_chart(year, state, yaxis, xaxis):
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
            yaxis = "CAP Local/All"
            fig = make_bubble_chart_fig(df2, year, yaxis, xaxis)
            fig.update_layout(title="No axis selected")
        elif len(yaxis) == 1:
            fig = make_bubble_chart_fig(df2, year, yaxis, xaxis)
            fig.update_layout(title=f"{yaxis[0]} vs. Democratic Performance")
            if yaxis[0] not in ["Total Nonwhite %", "CAP Local/All"]:
                fig.update_layout(
                    yaxis=dict(showgrid=False, tickformat=",.0f"),
                )
        else:
            df3 = create_combined_metrics(df2, *yaxis)
            fig = make_bubble_chart_fig(df3, year, "combined_metric", xaxis)
            fig.update_layout(
                title=f"{', '.join(yaxis)} Combined vs. Dem Performance",
                yaxis_title="Combined Metric Score",
                yaxis=dict(showgrid=False, tickformat=",.1f"),
            )
    else:
        fig = make_bubble_chart_fig(df2, year, yaxis, xaxis)
        fig.update_layout(title=f"{yaxis} vs. Dem Performance")
        if yaxis not in ["Total Nonwhite %", "CAP Local/All"]:
            fig.update_layout(
                yaxis=dict(showgrid=False, tickformat=",.0f"),
            )
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
