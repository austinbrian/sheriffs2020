import sys
from collections import OrderedDict

sys.path.append("..")
import plotly.graph_objects as go
import plotly.express as px
import dash_table.FormatTemplate as FormatTemplate

import pandas as pd
import numpy as np


df = pd.read_pickle("data/merged_data_sheriffs.pkl")
e18 = pd.read_pickle("data/elections_2018/attempt_4.pkl")


def yaxis_cols():
    return [
        {"label": l, "value": v}
        for l, v in [
            ("Immigration Enforcement", "CAP Local/All"),
            (
                "Deaths in Jail",
                "Deaths_per_thousand_pop",
            ),
            (
                "Detainers Total",
                "Detainers Total",
            ),
            (
                "Killings by Deputies",
                "killings_per_k_arrests",
            ),
            ("Total Nonwhite %", "Total Nonwhite %"),
        ]
    ]


def xaxis_cols():
    return [
        {"label": l, "value": v}
        for l, v in [
            ("Dem % 2020", "per_dem"),
            ("Dem % 2018", "Dem%"),
        ]
    ]


def set_table_style_cell_conditional():
    return [
        {
            "if": {"column_id": c},
            "textAlign": "right",
        }
        for c in [
            "per_dem",
            "sen",
            "CAP Local/All",
            "Detainers Total",
            "Deaths_per_thousand_pop",
            "killings_per_k_arrests",
        ]
    ]


party_colors = dict(
    zip(
        ["Nonpartisan", "Unknown", "Democratic Party", "Republican Party"],
        ["green", "gray", "blue", "red"],
    )
)


def make_bubble_chart_fig(df, year, yaxis, xaxis):
    df.loc[:, "votesize"] = df["total_votes"].apply(lambda x: x ** (1 / 2))
    df = df[df[f"has_election_{year}"]]
    df.loc[:, "Party Roll Up"] = df["Party Roll Up"].fillna("Unknown")
    if isinstance(xaxis, list):
        df["xaxis"] = df[xaxis].mean(axis=1)
    elif isinstance(xaxis, str):
        df.loc[:, "xaxis"] = df[xaxis]
    else:
        df["xaxis"] = df["per_dem"]

    fig = px.scatter(
        df,
        x="xaxis",
        y=yaxis,
        size="votesize",
        color="Party Roll Up",
        color_discrete_map=party_colors,
        hover_name="county_name",
        hover_data=OrderedDict(
            {
                "State": True,
                "xaxis": ":.2%",
                "CAP Local/All": ":0.2f",
                "votesize": False,
                "total_votes": ":,f",
                "Official Name": True,
                "Party Roll Up": True,
            }
        ),
        labels={
            "xaxis": "Democratic % for selected races",
            "total_votes": "2020 Total Votes",
            "Official Name": "Sheriff Name",
            "Party Roll Up": "Sheriff Party",
        },
    )

    fig.update_layout(
        {
            "plot_bgcolor": "rgba(245,245,245)",
            "paper_bgcolor": "rgba(245,245,245)",
            "xaxis": {"showgrid": False, "tickformat": ",.0%"},
            "yaxis": {"showgrid": False, "tickformat": ",.0%"},
        },
    )
    return fig


def make_table(df):
    pass


def make_table_columns(df):

    cols = [
        {"id": "statecode", "name": "ST", "type": "text", "hideable": True},
        {"id": "State", "name": "State", "type": "text"},
        {"id": "Electoral District", "name": "County", "type": "text"},
        {
            "id": "Office Name",
            "name": "Office",
            "type": "text",
            "format": {"specifier": ":.15s"},
            "hideable": True,
        },
        {"id": "Official Name", "name": "Sherriff Name", "type": "text"},
        {"id": "Party Roll Up", "name": "Party", "type": "text"},
        {
            "id": "per_dem",
            "name": "'20 Pres % Dem",
            "type": "numeric",
            "format": FormatTemplate.percentage(2),
        },
        {
            "id": "sen",
            "name": "'18 Sen % Dem",
            "type": "numeric",
            "format": FormatTemplate.percentage(2),
        },
        {
            "id": "CAP Local/All",
            "name": "CAP Local/All",
            "type": "numeric",
            "format": {"locale": {}, "nully": "", "specifier": ".2%"},
            "hideable": True,
        },
        {
            "id": "Detainers Total",
            "name": "Detainers Total",
            "type": "numeric",
            "format": {"specifier": ",.0f"},
            "hideable": True,
        },
        {
            "id": "Deaths_per_thousand_pop",
            "name": "Deaths per 1k jailed pop",
            "type": "numeric",
            "format": {"specifier": ".1f"},
            "hideable": True,
        },
        {
            "id": "killings_per_k_arrests",
            "name": "Killings per 1k arrests",
            "type": "numeric",
            "format": {"specifier": ",.1f"},
            "hideable": True,
        },
    ]

    return cols