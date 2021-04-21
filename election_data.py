import pandas as pd
from next_election import county_populations
from data_pipeline import merge_data


def get_state_df(state, jurisdiction="precinct"):
    stdf = pd.read_csv(
        f"https://github.com/openelections/openelections-data-{state}/blob/master/2018/20181106__{state}__general__{jurisdiction}.csv?raw=true".lower(),
        low_memory=False,
        thousands=",",
    )
    return stdf


def calc_perf_2018(n=3):
    full_df = pd.DataFrame()
    # md = merge_data()
    md = pd.read_pickle("data/processed_data/merge_data.pkl")
    states_22 = states_22 = md[md.has_election_2022].ST.dropna().unique()
    print("Need to create df for states:", states_22)
    counties = county_populations()[
        ["STNAME", "ST", "CTYNAME", "FIPS", "POPESTIMATE2019"]
    ]
    counties["simple_county"] = counties.CTYNAME.apply(
        lambda x: " ".join(x.split()[:-1]) if "county" in x.lower() else x
    )
    for state in states_22[:n]:
        try:
            stdf = get_state_df(state, "county")
        except:
            try:
                stdf = get_state_df(state, "precinct")
                stdf.dropna(subset=["county", "office", "votes"], inplace=True)
            except:
                print(f"No data found for {state}")
                continue
        print(f"creating {state}")
        if "Ballots Cast" in stdf.office.unique():
            stdf["votes"] = stdf["votes"].dropna().astype(int)
            ballots_dict = (
                stdf[stdf.office == "Ballots Cast"]
                .groupby("county")["votes"]
                .sum()
                .to_dict()
            )
        else:
            stdf["votes"] = stdf["votes"].dropna()
            ballots_dict = (
                stdf.groupby(["county", "office"])["votes"]
                .sum()
                .groupby("county")
                .max()
                .to_dict()
            )

        df = counties[counties.ST == state].copy()
        df["rec_ballots_18"] = df["simple_county"].map(ballots_dict)

        # other stuff

        try:

            partycols = (
                stdf.groupby(["county", "party"])["votes"].sum().unstack().reset_index()
            )
            df = df.merge(partycols, left_on="simple_county", right_on="county")

        except:
            continue

        full_df = pd.concat([full_df, df])

    return full_df


def nevada_18():
    NV = get_state_df("NV")
    # US Sen, Gov, Lt. Gov, AG
    nv_electeds = {
        "ROSEN, JACKY": "DEM",
        "Heller, Dean": "REP",
        "SISOLAK, STEVE": "DEM",
        "LAXALT, ADAM PAUL": "REP",
        "MARSHALL, KATE": "DEM",
        "ROBERSON, MICHAEL": "REP",
        "FORD, AARON": "DEM",
        "DUNCAN, WES": "REP",
    }
    NV["party"] = NV.candidate.map(nv_electeds)
    nvg = NV.groupby(["county", "office", "party"])["votes"].sum().unstack()
    nvg["tot_vot"] = NV.groupby(["county", "office"])["votes"].sum()
    nvg["Dem%"] = nvg["DEM"] / nvg["tot_vot"]
    # return nvg.groupby("county")["Dem%"].mean()
    return nvg


if __name__ == "__main__":
    xf = calc_perf_2018(n=100)
    xf.to_pickle("data/elections_2018/attempt_1.pkl")
