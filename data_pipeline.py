from datetime import datetime
import pandas as pd
import us

import imm_scraper as im


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


def election_counties_2020():
    elex = pd.read_csv(
        "https://raw.githubusercontent.com/tonmcg/US_County_Level_Election_Results_08-20/master/2020_US_County_Level_Presidential_Results.csv",
        dtype={"county_fips": str},
    )

    # have to rewrite this to be positive dems, negative if GOP wins
    # bc my brain is broken otherwise

    elex["diff"] = elex["diff"] * -1
    elex["per_point_diff"] = elex["per_point_diff"] * -1
    return elex


def county_populations():
    countypop = pd.read_csv(
        "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv",
        encoding="ISO-8859-1",
        usecols=[
            "SUMLEV",
            "REGION",
            "DIVISION",
            "STATE",
            "COUNTY",
            "STNAME",
            "CTYNAME",
            "POPESTIMATE2019",
            "INTERNATIONALMIG2019",
            "NETMIG2019",
        ],
        dtype={"STATE": str, "COUNTY": str},
    )
    countypop["ST"] = countypop["STNAME"].map((us.states.mapping("name", "abbr")))
    countypop["FIPS"] = countypop["STATE"].str.pad(2, fillchar="0") + countypop[
        "COUNTY"
    ].str.pad(3, fillchar="0")
    # get rid of state summary lines
    countypop = countypop[countypop.SUMLEV == 50]
    # check that it has all 50 states and DC
    assert countypop.ST.nunique() == 51
    return countypop


def get_va_cities(df, county_field="CTYNAME", state_field="STNAME"):
    virginia_cities = [
        i
        for i in df[df[state_field] == "Virginia"][county_field].unique()
        if "city" in i.lower()
        if "county" not in i.lower()
    ]
    # yes, virginia. you have two "Confederate City County" names. you did bad and you should feel bad.
    try:
        assert len(virginia_cities) == 38
    except AssertionError as e:
        print(len(virginia_cities))
        raise (e)
    return virginia_cities


def mark_has_elex(
    df,
    countydict,
    year=2021,
    county_field="CTYNAME",
    state_field="STNAME",
    colname="has_election_",
):
    elec_field = colname + str(year)
    df[elec_field] = False

    if year == 2021:
        virginia_cities = get_va_cities(df, county_field, state_field)
    county_counter = 0
    for state in countydict:
        countydict[state] = [i + " County" for i in countydict[state]]

    countydict["Virginia"] = virginia_cities
    countydict["Louisiana"] = ["Orleans Parish"]

    for state in countydict:
        for county in countydict[state]:
            df.loc[
                (df[state_field] == state) & (df[county_field] == county), elec_field
            ] = True
            county_counter += 1

    try:
        assert len(df[df[elec_field]]) == county_counter
    except AssertionError as e:
        print(county_counter, len(df[df[elec_field]]))
        raise (e)

    return df


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
    # inplace=True doesn't work here, which isn't great
    df["d1619"] = df.apply(lambda x: x.d2016 + x.d2017 + x.d2018 + x.d2019, axis=1)
    return df


def deaths_data():
    """Individual deaths and causes"""
    rdtypes = {"id": str, "fips": str, "year": int}
    df = pd.read_csv("../data/reuters/all_jails.csv", encoding="cp1252", dtype=rdtypes)
    return df


def reuters_codesheet():
    return pd.read_excel(
        "../data/reuters/reuters-jail-deaths-codesheets.xlsx", skiprows=2
    )


def arrest_data(grouped=True):
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
    return arr


def merge_data():
    elex = election_counties_2020()
    jails = jails_data()
    elex["statecode"] = elex["state_name"].map(dict(zip(jails.state, jails.statecode)))
    jails["d_1619"] = (
        jails["fips"].map(jails.groupby("fips")["d1619"].sum().to_dict()).fillna(0)
    )
    df = elex.merge(
        jails[["fips", "d_1619"]],
        how="left",
        left_on="county_fips",
        right_on="fips",
    )
    arr = arrest_data(grouped=True)
    df = df.merge(
        arr[["County/Surrounding Area", "CAPLocal_1619", "County", "ST"]],
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
    # now for the big part, merging with detainers
    md = MergedDetainers().dropna()

    # limit to just 2016 or later and only county facilities
    md = md[(md.Year >= 2016) & (md["Facility Type"] == "County Facility")]
    md["Detainers Total"] = md.County.map(md.groupby("County")["Total"].sum().to_dict())
    df = df.merge(
        md[["State", "County", "Detainers Total"]],
        how="left",
        left_on=["state_name", "county_name"],
        right_on=["State", "County"],
    )

    # money column: cap local / total detainers
    df["CAP Local/Detainers"] = df["CAPLocal_1619"] / df["Detainers Total"]

    df.drop(["County_x", "County_y"], axis=1, inplace=True)
    return df.drop_duplicates()


if __name__ == "__main__":
    merge_data()
