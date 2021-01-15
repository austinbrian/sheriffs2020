from datetime import datetime
import pandas as pd
import us


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
    elex["dem_adv"] = elex["votes_dem"] - elex["votes_gop"]
    elex["dem_adv_pct"] = elex["votes_dem"] / elex["total_votes"]
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
    )
    countypop["ST"] = countypop["STNAME"].map((us.states.mapping("name", "abbr")))
    # get rid of state summary lines
    countypop = countypop[countypop.SUMLEV == 50]
    # check that it has all 50 states and DC
    assert countypop.ST.nunique() == 51
    return countypop


def get_va_cities(df):
    virginia_cities = [
        i
        for i in df[df.STNAME == "Virginia"]["CTYNAME"].unique()
        if "city" in i.lower()
        if "county" not in i.lower()
    ]
    # yes, virginia. you have two "Confederate City County" names. you did bad and you should feel bad.
    assert len(virginia_cities) == 38
    return virginia_cities


def mark_has_elex(
    df, countydict, year=2021, countyname="CTYNAME", colname="has_election_"
):
    elec_field = colname + str(year)
    df[elec_field] == False

    if year == 2021:
        virginia_cities = get_va_cities(df)
    county_counter = 0
    for state in countydict:
        countydict[state] = [i + " County" for i in countydict[state]]

    countydict["Virginia"] = virginia_cities
    countydict["Louisiana"] = ["Orleans Parish"]

    for state in countydict:
        for county in countydict[state]:
            df.loc[(df.STNAME == state) & (df[countyname] == county), elec_field] = True
            county_counter += 1

    assert len(df[df[elec_field]]) == county_counter

    return df


def jails_data():
    rdtypes = {"id": str, "fips": str, "year": int}
    df = pd.read_csv("../data/reuters/all_jails.csv", encoding="cp1252", dtype=rdtypes)
    df["fips"] = df["fips"].str.pad(5, fillchar="0")
    return df


def deaths_data():
    rdtypes = {"id": str, "fips": str, "year": int}
    df = pd.read_csv("../data/reuters/all_jails.csv", encoding="cp1252", dtype=rdtypes)
    df["fips"] = df["fips"].str.pad(5, fillchar="0")
    return df


def reuters_codesheet():
    return pd.read_excel(
        "../data/reuters/reuters-jail-deaths-codesheets.xlsx", skiprows=2
    )


def arrest_data():
    arr = pd.read_csv("../data/arrest_data.csv")
