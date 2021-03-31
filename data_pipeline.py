from datetime import datetime
import pandas as pd
import numpy as np
import os
import us

import imm_scraper as im
from next_election import *


dir_path = os.path.dirname(os.path.realpath(__file__))


class MonthlyDetainers:
    def __new__(cls=pd.DataFrame):
        # Need to bring together the Georgia and Florida dfs
        dtypes = {"Year": int}
        gdf = pd.read_csv(
            "../data/state_total_Georgia.csv", thousands=",", dtype=dtypes
        ).drop("Unnamed: 0", axis=1)
        fdf = pd.read_csv(
            "../data/state_total_Florida.csv", thousands=",", dtype=dtypes
        ).drop("Unnamed: 0", axis=1)
        mdf = gdf.append(fdf)

        # Drop where facility or year-month==all
        mdf = mdf[(mdf.Facility != "All") & (mdf["Year-Month"] != "All")]

        mdf.reset_index(drop=True, inplace=True)

        ddf = convert_year_month(mdf)
        ddf = split_jurisdictions(ddf)
        ddf = sort_cols(
            ddf,
            ["State", "County", "Facility", "Total", "Month", "Year", "Facility_Raw"],
        )

        return ddf


def group_annual(df):
    return (
        df.groupby(["State", "County", "Facility", "Facility_Raw", "Year"])["Total"]
        .sum()
        .to_frame()
        .reset_index()
    )


class MergedDetainers:
    def __new__(cls=pd.DataFrame):
        annual = AnnualDetainers()
        monthly = MonthlyDetainers()
        gdf = group_annual(monthly)
        mdf = gdf.merge(
            annual[
                [
                    "County-Facility Detainer Sent",
                    "Fiscal Year",
                    "Facility Type",
                ]
            ],
            how="left",
            left_on="Facility_Raw",
            right_on="County-Facility Detainer Sent",
        ).drop(["Fiscal Year", "County-Facility Detainer Sent"], axis=1)
        mdf = mdf.merge(
            annual[
                [
                    "County-Facility Detainer Sent",
                    "Fiscal Year",
                    "Detainer Refused-No",
                    "Detainer Refused-Yes",
                    "Detainer Refused-Not Known",
                    "Notice (Not Detainer) Issued-Yes",
                ]
            ],
            how="left",
            left_on=["Facility_Raw", "Year"],
            right_on=["County-Facility Detainer Sent", "Fiscal Year"],
        ).drop(["Fiscal Year"], axis=1)
        mdf["Year"] = mdf["Year"].astype(int)
        return mdf


class AnnualDetainers:
    def __new__(cls=pd.DataFrame):
        df = pd.read_csv("../data/total_yearly_data.csv", thousands=",")
        ddf = sort_cols(
            df,
            [
                "County-Facility Detainer Sent",
                "Total Detainers",
                "Fiscal Year",
                "State",
                "Facility Type",
                "Male",
                "Female",
            ],
            True,
            "Detainer Refused",
            "Notice (Not Detainer)",
            "ICE Assumed",
            "Age Group",
        )
        return ddf


def convert_year_month(df):
    df["date"] = df["Year-Month"].apply(lambda x: datetime.strptime(x, "%Y-%m"))
    df["Month"] = df.date.dt.strftime("%B")
    df["Year"] = df.date.dt.strftime("%Y")

    return df


def split_jurisdictions(df, facility="Facility"):
    if facility == "Facility":
        df["Facility_Raw"] = df["Facility"].copy()
    df["jdictsplit"] = df[facility].str.split(" - ")
    df["County"] = df.jdictsplit.apply(lambda x: x[0])
    df["Facility"] = df.jdictsplit.apply(lambda x: x[1])

    return df.drop("jdictsplit", axis=1)


def sort_cols(df, pref: list = [], remove: bool = True, *args):
    for i in pref:
        if i in df.columns:
            continue
        else:
            pref.extend([i for i in df.columns if i in pref])

    grouped_cols = []

    if args:
        for a in args:
            l = list(filter(lambda x: a.lower() in x.lower(), df.columns))
            grouped_cols.extend(l)

    col_list = (
        pref
        + grouped_cols
        + sorted(list(filter(lambda x: x not in pref + grouped_cols, df.columns)))
    )
    if remove:
        col_list = list(filter(lambda x: x in pref + grouped_cols, df.columns))

    return df[col_list]


def jails_data():
    rdtypes = {"id": str, "fips": str, "year": int}
    df = pd.read_csv("../data/reuters/all_jails.csv", encoding="cp1252", dtype=rdtypes)
    df["fips"] = df["fips"].str.pad(5, fillchar="0")
    # sum the deaths from 2016-2019
    df[["d2016", "d2017", "d2018", "d2019",]] = df[
        [
            "d2016",
            "d2017",
            "d2018",
            "d2019",
        ]
    ].fillna(0)
    df[["adp2016", "adp2017", "adp2018", "adp2019",]] = df[
        [
            "adp2016",
            "adp2017",
            "adp2018",
            "adp2019",
        ]
    ].fillna(0)
    # inplace=True doesn't work here, which isn't great
    df["d1619"] = df.apply(lambda x: x.d2016 + x.d2017 + x.d2018 + x.d2019, axis=1)
    df["total_adp1619"] = df.apply(
        lambda x: x.adp2016 + x.adp2017 + x.adp2018 + x.adp2019, axis=1
    )  # to get number of years -- sometimes 0 fills in, not what we want
    df["yrs_adp1619"] = df.apply(
        lambda x: len(
            [l for l in [x.adp2016, x.adp2017, x.adp2018, x.adp2019] if l > 0]
        ),
        axis=1,
    )
    # it turns out we can drop anything with yrs_adp1619<1
    df.drop(df[df.yrs_adp1619 < 1].index, inplace=True)

    df["avg_adp1619"] = df["total_adp1619"] / df["yrs_adp1619"]
    df["Deaths_per_thousand_pop"] = df["d1619"] / df["avg_adp1619"] * 1000.0
    df.drop(["total_adp1619", "yrs_adp1619"], axis=1, inplace=True)
    return df


def deaths_data():
    """Individual deaths and causes
    introduce deaths per adp
    roll it up 16-19
    """
    rdtypes = {"id": str, "fips": str, "year": int}
    df = pd.read_csv("../data/reuters/all_jails.csv", encoding="cp1252", dtype=rdtypes)
    return df


def reuters_codesheet():
    return pd.read_excel(
        "../data/reuters/reuters-jail-deaths-codesheets.xlsx", skiprows=2
    )


def imm_arrest_data(grouped=True):
    arr = pd.read_csv("../data/arrest_data.csv", thousands=",")
    arr["c_area_split"] = arr["County/Surrounding Area"].str.split(", ")
    arr["lensplit"] = arr["c_area_split"].apply(lambda x: len(x))
    arr = arr[arr.lensplit > 1]
    arr["County"] = arr.c_area_split.apply(lambda x: x[0])
    arr["ST"] = arr.c_area_split.apply(lambda x: x[1])
    arr.drop(["c_area_split", "lensplit"], axis=1, inplace=True)
    if grouped:
        arr = arr[arr["Fiscal Year"].isin([2016, 2017, 2018, 2019])]
        arr["CAPLocal_1619"] = arr["County/Surrounding Area"].map(
            arr.groupby("County/Surrounding Area")["CAP Local Incarceration"]
            .sum()
            .to_dict()
        )
        arr["All_1619"] = arr["County/Surrounding Area"].map(
            arr.groupby("County/Surrounding Area")["All"].sum().to_dict()
        )
    return arr


def total_arrest_data():
    arr = pd.read_csv(
        "../data/ICPSR_37056/DS0001/37056-0001-Data.tsv", sep="\t", low_memory=False
    )
    # this dataset has some wild choices for missing data
    # mostly it's 99998 or 99999, but there's a few special cases to handle
    colvals = [
        "STNAME",
        "AGENCY",
        "ORI",
        "MSA",
        "POP",
        "OFFENSE",
        "OCCUR",
        "MONTH",
        "MOHEADER",
        "AW",
        "AB",
        "AI",
        "AA",
        "JW",
        "JB",
        "JI",
        "JA",
        "AH",
        "AN",
    ] + "M0_9	M10_12	M13_14	M15	M16	M17	M18	M19	M20	M21	M22	M23	M24	M25_29	M30_34	M35_39	M40_44	M45_49	M50_54	M55_59	M60_64	M65	F0_9	F10_12	F13_14	F15	F16	F17	F18	F19	F20	F21	F22	F23	F24	F25_29	F30_34	F35_39	F40_44	F45_49	F50_54	F55_59	F60_64	F65".split(
        "\t"
    )
    nancols = [
        "MONTH",
        "MOHEADER",
        "OFFENSE",
        "OCCUR",
    ]
    colnans = [
        98,
        [998, 0],
        [998, "998"],
        998,
    ]
    arr = (
        arr[colvals]
        .replace([99999, 99998], np.nan)
        .replace(dict(zip(nancols, colnans)), np.nan)
    )
    # no better way, seemingy of getting this info, so we're just going to sum race
    arr["adult_arrests"] = arr[["AW", "AB", "AI", "AA"]].sum(axis=1)
    arr["juv_arrests"] = arr[["JW", "JB", "JI", "JA"]].sum(axis=1)
    # and all Hispanic markers are NaN in this dataset??
    arr["tot_arrests"] = arr.adult_arrests + arr.juv_arrests
    return arr


def flatten(lis):
    for item in lis:
        if isinstance(item, list) and not isinstance(item, str):
            for x in flatten(item):
                yield x
        else:
            yield item


def unstack_multi_jurisdictions(tst):
    mdf = tst.loc[np.repeat(tst.index.values, tst.num_jurisdictions.astype(int))]
    juris = list(
        flatten(
            tst.loc[:, "ORI Agency Identifier (if available)"].str.split(";").values
        )
    )
    mdf["ori"] = juris
    return mdf


def police_killings():
    mpv = pd.read_csv(
        "../data/MPVDatasetDownload.xlsx - 2013-2020 Police Killings.csv",
        low_memory=False,
    )
    # there is just one weird NaN jurisdiction here -- the Burlington Northern Santa Fe Railway PD, in Denver
    mpv = mpv[mpv["ORI Agency Identifier (if available)"].notna()]
    mpv["num_jurisdictions"] = mpv["ORI Agency Identifier (if available)"].apply(
        lambda x: len(x.split(";"))
    )
    mpv["long_ori"] = mpv["ORI Agency Identifier (if available)"]
    # duplicate multi-jurisdiction shootings
    mpv = unstack_multi_jurisdictions(mpv)
    # drop federal jurisdictions
    mpv = mpv[~mpv["ori"].apply(lambda x: x[-2:] != "00")]
    # drop the double zero
    mpv["ori"] = mpv.ori.apply(lambda x: x[:-2])
    # most recent data is for 2016, and "POP" is the population for the facility for the full year
    arr = total_arrest_data()
    mpv["pop_jailed_2016"] = mpv.ori.map(arr.groupby(["ORI"])["POP"].max().to_dict())
    mpv["arrests_2016"] = mpv.ori.map(arr.groupby("ORI")["tot_arrests"].sum().to_dict())

    # it looks like the national scorecard file is a better source for this
    # nsd = nationwide_scorecard_database()
    # mpv = mpv.merge(nsd, left_on="ORI Agency Identifier (if available)", right_on="ori")

    return mpv


def shootings_per_1k_arrests():
    mpv = police_killings()
    spka = (
        mpv[
            [
                "City",
                "State",
                "County",
                "ori",
                "MPV ID",
                "arrests_2016",
                "pop_jailed_2016",
            ]
        ]
        .groupby(
            [
                "State",
                "County",
                "ori",
            ]
        )
        .agg({"MPV ID": "count", "arrests_2016": sum, "pop_jailed_2016": max})
        .reset_index()
    )
    spka["shootings_per_k_arr"] = spka["MPV ID"] / (spka["arrests_2016"] / 1000)
    spka["shot_per_jailed_pop"] = spka["MPV ID"] / (spka["pop_jailed_2016"] / 1000)
    spka.replace(
        {"shootings_per_k_arr": np.inf, "shot_per_jailed_pop": np.inf},
        np.nan,
        inplace=True,
    )
    return spka.sort_values(by="shootings_per_k_arr", ascending=False)


def nationwide_scorecard_database(**kwargs):
    """
    https://docs.google.com/spreadsheets/d/10zEUA5l2-4_bo0HPxUULJ81KIDPnDkL2OxYuqFoJ8zU/edit#gid=1623145710
    """
    df = pd.read_csv(
        os.path.join(dir_path, "data/Nationwide_Scorecard_Database.csv"),
        converters={
            "fips_state_code": lambda x: "{:02d}".format(int(x)),
            "fips_county_code": lambda x: "{:03d}".format(int(x)),
        },
        low_memory=False,
        **kwargs
    )
    df["fips"] = df["fips_state_code"] + df["fips_county_code"]
    df["total_arrests"] = df[
        "arrests_2013,arrests_2014,arrests_2015,arrests_2016,arrests_2017,arrests_2018".split(
            ","
        )
    ].sum(axis=1)
    # for our purposes we are only interested in the sheriff agencies

    return df


def merge_data():
    elex = election_counties_2020()
    jails = jails_data()
    elex["statecode"] = elex["state_name"].map(dict(zip(jails.state, jails.statecode)))
    # jails["d_1619"] = (
    #     jails["fips"].map(jails.groupby("fips")["d1619"].sum().to_dict()).fillna(0)
    # )

    # multiple facilities in several counties so this adds them
    jdf = (
        jails[
            [
                "fips",
                "d2016",
                "d2017",
                "d2018",
                "d2019",
                "adp2016",
                "adp2017",
                "adp2018",
                "adp2019",
                "d1619",
            ]
        ]
        .groupby("fips")
        .sum()
        .reset_index()
    )
    jdf["avg_adp_1619"] = jdf[["adp2016", "adp2017", "adp2018", "adp2019"]].apply(
        lambda x: np.mean(x[x != 0]), axis=1
    )
    jdf["Deaths_per_thousand_pop"] = jdf["d1619"] / jdf["avg_adp_1619"] * 1000.0
    df = elex.merge(
        jails[["fips", "d1619", "avg_adp1619", "Deaths_per_thousand_pop"]],
        how="left",
        left_on="county_fips",
        right_on="fips",
    ).drop("fips", axis=1)
    arr = imm_arrest_data(grouped=True)
    df = df.merge(
        arr[["County/Surrounding Area", "CAPLocal_1619", "County", "ST", "All_1619"]],
        how="left",
        left_on=["county_name", "statecode"],
        right_on=["County", "ST"],
    ).drop_duplicates()
    df = mark_has_elex(
        df,
        im.get_2021_counties(),
        year=2021,
        county_field="county_name",
        state_field="state_name",
    )
    # add in a column for 2022
    df["has_election_2022"] = df.county_fips.map(
        has_2022_elex().set_index("FIPS")["has_election_2022"].to_dict()
    )

    # now for the big part, merging with detainers
    md = MergedDetainers().dropna()

    # limit to just 2016 or later and only county facilities
    md = md[(md.Year >= 2016) & (md["Facility Type"] == "County Facility")]
    md["county_lower"] = md.County.str.lower()
    df["county_lower"] = df.county_name.str.lower()
    md["Detainers Total"] = md.County.map(md.groupby("County")["Total"].sum().to_dict())
    df = df.merge(
        md[["State", "county_lower", "Detainers Total"]],
        left_on=["state_name", "county_lower"],
        right_on=["State", "county_lower"],
    )
    # money column: cap local / total detainers
    df["CAP Local/Detainers"] = df["CAPLocal_1619"] / df["Detainers Total"]

    ### don't use Total Detainers, instead use "All" from arrests data
    ## TODO: assert that this falls between 0 and 1
    df["CAP Local/All"] = df["CAPLocal_1619"] / df["All_1619"]

    # add in arrest columns from national scorecard
    nsd = nationwide_scorecard_database()

    # # also want shooting data to be in scorecard
    mpv = police_killings()
    nsd["killings"] = nsd["ori"].map(
        mpv.groupby("long_ori")["MPV ID"].count().to_dict()
    )
    gnsd = (
        nsd.groupby("fips")[
            list(filter(lambda x: "arrest" in x, nsd.columns)) + ["killings"]
        ]
        .sum()
        .reset_index()
    )
    gnsd["killings_per_k_arrests"] = gnsd["killings"] / (gnsd["total_arrests"] / 1000)
    gnsd["low_level_per_arrest"] = gnsd["low_level_arrests"] / gnsd["total_arrests"]

    df["killings_per_k_arrests"] = df.county_fips.map(
        gnsd.set_index("fips")["killings_per_k_arrests"].to_dict()
    )
    df["low_level_per_arrest"] = df.county_fips.map(
        gnsd.set_index("fips")["low_level_per_arrest"].to_dict()
    )

    return df.drop_duplicates()


def wholeads_data(group: str = "electeds"):
    url = "https://wholeads.us/wp-content/uploads/2020/06/Sheriffs-Report-Data.xlsx"

    def get_electeds():
        who = pd.read_excel(url, sheet_name="Electeds Raw")
        who["mult_jurisdictions"] = who["Electoral District"].str.split(" & ")
        who["num_jurisdictions"] = who.mult_jurisdictions.apply(lambda x: len(x))
        who["adj_county"] = who["Electoral District"].copy()

        # duplicates the multi-jurisdictions
        mdf = who.loc[np.repeat(who.index.values, who.num_jurisdictions.astype(int))][
            who.num_jurisdictions > 1
        ]
        s = mdf.mult_jurisdictions.values.tolist()
        l = list(flatten(s))
        mdf.adj_county = sorted(set(l), key=l.index)
        electeds = pd.concat([who.drop(who[who.num_jurisdictions > 1].index), mdf])
        electeds["county_lower"] = electeds.adj_county.str.lower()
        return electeds

    def get_candidates():
        cands = pd.read_excel(
            url,
            sheet_name="Candidates Raw",
            usecols=[
                "RDIndex2019",
                "Candidate UUID",
                "State",
                "Office Level",
                "OCDID",
                "Electoral District",
                "Office UUID",
                "Unopposed",
                "Office Name",
                "Seat ID",
                "Number Elected",
                "Candidate Name",
                "Candidate Party",
                "Party ID Roll Up",
                "White/Non-White",
                "Race",
                "Gender",
                "Winner Y/N",
            ],
        )
        return cands

    if group.lower() == "electeds":
        return get_electeds()
    elif group.lower() == "candidates":
        return get_candidates()
    else:
        return {"electeds": get_electeds(), "candidates": get_candidates()}


if __name__ == "__main__":
    who = wholeads_data("electeds")
    who["county_lower"]
    merge_data().merge(
        who.rename({"State": "statecode"}, axis=1).drop("Total", axis=1),
        left_on=["statecode", "county_name"],
        right_on=["statecode", "Electoral District"],
    ).drop_duplicates().to_pickle(os.path.join(dir_path, "data", "merged_data.pkl"))
