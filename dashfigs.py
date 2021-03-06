import sys
import math

sys.path.append("..")
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd

# df = pd.read_pickle("data/merged_data.pkl")


def make_fig(df):
    df["votesize"] = df["total_votes"].apply(lambda x: math.sqrt(x))
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
        labels={"per_dem": "Dem %", "total_votes": "2020 Total Votes"},
    )

    fig.update_layout(
        {
            "plot_bgcolor": "rgba(245,245,245)",
            "paper_bgcolor": "rgba(245,245,245)",
            # "paper_bgcolor": "rgba(0,0,0,0)",
            "xaxis": {"showgrid": False},
            "yaxis": {"showgrid": False},
        },
    )
    return fig
