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


def process_party_names(stdf):
    xf = (
        stdf.groupby(["county", "office", "party"])["votes"]
        .sum()
        .unstack()
        .reset_index()
    )
    xf["tot_vot"] = xf.sum(axis=1, numeric_only=True)
    # xf["state"] = state
    dem_names = [
        "DEM",
        "Dem",
        "Democtratic",
        "DemocraticOCRATIC",
        "Democratic",
        "Democratic Party",
        "DFL",
        "WFP",
        "Working Families",
        "WOR",
        "Women's Equality",
        "Women's Equality Party",
    ]
    rep_names = [
        "REP",
        "Republican",
        "Rep",
        "Republican Party",
        "GOP",
        "GOP.",
        "R",
    ]
    other_names = [
        x
        for x in filter(
            lambda y: y not in ["party", "county", "office", "state"], xf.columns
        )
        if x not in dem_names + rep_names
    ]
    xf["D_r"] = (
        xf[filter(lambda x: x in dem_names, xf.columns)].astype(float).sum(axis=1)
    )
    xf["R_r"] = (
        xf[filter(lambda x: x in rep_names, xf.columns)]
        .astype(float)
        .sum(
            axis=1,
        )
    )
    # xf["O_r"] = (
    #     xf[filter(lambda x: x in other_names, xf.columns)].astype(float).sum(axis=1)
    # )
    xf["O_r"] = xf["tot_vot"] - xf["D_r"] - xf["R_r"]
    xfg = xf[
        filter(
            lambda x: x
            in ["party", "county", "office", "tot_vot", "D_r", "R_r", "O_r"],
            xf.columns,
        )
    ].copy()

    xfg.rename({"D_r": "DEM", "R_r": "REP", "O_r": "OTH"}, axis=1, inplace=True)
    xfg.loc[:, "Dem%"] = xfg["DEM"] / xfg["tot_vot"]
    return xfg


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
        if state in ["NH", "NV"]:
            if state == "NH":
                xf = new_hampshire_18()
            elif state == "NV":
                xf = nevada_18()
            df = counties[counties.ST == state].copy()
            df = df.merge(xf, left_on="simple_county", right_on="county")
            full_df = pd.concat([full_df, df])
            print("Wrote", state)
            continue
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
        stdf = stdf[
            stdf.office.str.upper().isin(
                ["U.S. SENATE", "GOVERNOR", "LIEUTENANT GOVERNOR", "ATTORNEY GENERAL"]
            )
        ]
        xf = process_party_names(stdf)
        xf["state"] = state

        df = df.merge(xf, left_on="simple_county", right_on="county")

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
    nvg["state"] = "NV"
    return nvg.reset_index()


def new_hampshire_18():
    nh = get_state_df("NH")
    nh = nh.dropna(subset=["votes"])
    nh = nh.drop(nh[nh.votes == " "].index)
    nh["votes"] = nh.votes.apply(lambda x: x.strip()).astype(int)
    nhg = (
        nh[nh.county.str.contains(" NH")]
        .groupby(["office", "county", "party"])["votes"]
        .sum()
        .unstack()
        .reset_index()
    )
    nhg["tot_vot"] = nhg["county"].map(
        nh[nh.county.str.contains(" NH")].groupby("county")["votes"].sum().to_dict()
    )
    nhg["county"] = nhg.county.str.rstrip(" NH")
    nhg.rename({"LBT": "OTH"}, axis=1, inplace=True)
    nhg["Dem%"] = nhg["DEM"] / nhg["tot_vot"]
    nhg["state"] = "NH"
    return nhg


if __name__ == "__main__":
    xf = calc_perf_2018(n=100)
    xf.to_pickle("data/elections_2018/attempt_3.pkl")
    # nh = new_hampshire_18()
    # nv = nevada_18()
    # pd.concat([xf, nh, nv]).to_pickle("data/elections_2018/attempt_2.pkl")
