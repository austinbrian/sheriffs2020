import sys

sys.path.append("..")
import plotly.graph_objects as go
import plotly.express as px
import dash_table.FormatTemplate as FormatTemplate

import pandas as pd


# df = pd.read_pickle("data/merged_data.pkl")


def make_bubble_chart_fig(df):
    df["votesize"] = df["total_votes"].apply(lambda x: x ** (1 / 2))
    fig = px.scatter(
        df,
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
        labels={
            "per_dem": "Dem %",
            "total_votes": "2020 Total Votes",
            "Official Name": "Sheriff Name",
            "Party Roll Up": "Party",
        },
    )

    fig.update_layout(
        {
            "plot_bgcolor": "rgba(245,245,245)",
            "paper_bgcolor": "rgba(245,245,245)",
            "xaxis": {"showgrid": False, "tickformat": ",.0%"},
            "yaxis": {"showgrid": False},
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
            "format": {"specifier": ":.15"},
            "hideable": True,
        },
        {"id": "Official Name", "name": "Sherriff Name", "type": "text"},
        {"id": "Party Roll Up", "name": "Party", "type": "text"},
        {
            "id": "per_dem",
            "name": "% Dem",
            "type": "numeric",
            "format": FormatTemplate.percentage(2),
        },
        {
            "id": "CAP Local/All",
            "name": "CAP Local/All",
            "type": "numeric",
            "format": FormatTemplate.percentage(2),
        },
        {
            "id": "Detainers Total",
            "name": "Detainers Total",
            "type": "numeric",
            "format": {"specifier": ",.0f"},
        },
        {
            "id": "Deaths_per_thousand_pop",
            "name": "Deaths per 1k jailed pop",
            "type": "numeric",
            "format": {"specifier": ".1f"},
        },
        {
            "id": "killings_per_k_arrests",
            "name": "Killings per 1k arrests",
            "type": "numeric",
            "format": {"specifier": ",.1f"},
        },
    ]

    return cols