import pandas as pd
from datetime import datetime

# Need to bring together the Georgia and Florida dfs
def prep():
    """Bring together the Georgia and Florida dfs.
    Also drop the weird cols and whatever else"""
    gdf = pd.read_csv("../data/state_total_Georgia.csv", thousands=",").drop(
        "Unnamed: 0", axis=1
    )
    fdf = pd.read_csv("../data/state_total_Florida.csv", thousands=",").drop(
        "Unnamed: 0", axis=1
    )
    mdf = gdf.append(fdf)
    mdf

    # Drop where facility or year-month==all
    mdf = mdf[(mdf.Facility != "All") & (mdf["Year-Month"] != "All")]

    mdf.reset_index(drop=True, inplace=True)

    return mdf


def convert_year_month(df):
    df["date"] = df["Year-Month"].apply(lambda x: datetime.strptime(x, "%Y-%m"))
    df["Month"] = df.date.dt.strftime("%B")
    df["Year"] = df.date.dt.strftime("%Y")

    return df


def split_jurisdictions(df):
    df["jdictsplit"] = df["Facility"].str.split(" - ")
    df["County"] = df.jdictsplit.apply(lambda x: x[0])
    df["Facility"] = df.jdictsplit.apply(lambda x: x[1])

    return df.drop("jdictsplit", axis=1)
