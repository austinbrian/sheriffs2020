import pandas as pd


e18 = pd.read_pickle("data/elections_2018/attempt_4.pkl")


def create_combined_metrics(
    odf,
    *args,
):
    df = odf.copy()
    for col in args:
        df["z_" + col] = (df[col] - df[col].mean()) / df[col].std()
    df["combined_score"] = (
        df[[i for i in df.columns if "z_" in i]].fillna(0).sum(axis=1)
    )
    df["combined_metric"] = df["combined_score"] + abs(min(df["combined_score"]))
    return df


def combine_18_races(df, *args):
    rdf = e18[e18.FIPS.isin(df.FIPS)]
    if not args:
        return rdf.groupby("county")["Dem%"].mean()
    else:
        return (
            rdf[rdf.office.str.upper().isin(args.upper())]
            .groupby("county")["Dem%"]
            .mean()
        )


# def create_combined_xaxis(odf, *args):
#     odf['DemPerf'] =
