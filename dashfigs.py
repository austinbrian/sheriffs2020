import sys

sys.path.append("..")
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd

# df = pd.read_pickle("data/merged_data.pkl")


def make_fig(df):
    fig = px.scatter(
        df,
        x="per_dem",
        y="CAP Local/All",
        size="total_votes",
        color="per_dem",
        hover_data=["Electoral District", "statecode"],
    )
    return fig
