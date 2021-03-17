import pandas as pd


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