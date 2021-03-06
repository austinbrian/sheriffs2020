import pandas as pd
import us


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

    # try:
    #     assert len(df[df[elec_field]]) == county_counter
    # except AssertionError as e:
    #     print(county_counter, len(df[df[elec_field]]))
    #     raise (e)

    return df


def has_elex(year=2022):
    """WIP: refactor of the other has elex functions"""
    df = county_populations()
    has_elex_col = f"has_election_{year}"
    full_states = [
        "AL",
        "CA",
        "CO",
        "IL",
        "IN",
        "KY",
        "ME",
        "MD",
        "MI",
        "MA",
        "MN",
        "MT",
        "NE",
        "NV",
        "NH",
        "NM",
        "NC",
        "SD",
        "TN",
        "UT",
        "WA",
        "WI",
        "WY",
    ]

    # SD --> Every county "with an election is on the midterm cycle" ??

    true_county_dict = {
        "DE": ["Sussex County", "New Castle County"],
        "NJ": [
            i.strip() + " County"
            for i in "Burlington, Hudson, Hunterdon, Middlesex, Monmouth, Morris, Ocean, Passaic, Somerset, Sussex, Warren".split(
                ","
            )
        ],
        "NY": [
            i.strip() + " County"
            for i in "Allegany, Broome, Cayuga, Chautauqua, Clinton, Delaware, Essex, Franklin, Jefferson, Montgomery, Oneida, Onondaga, Ontario, Orange, Oswego, Otsego, Tompkins, Ulster".split(
                ","
            )
        ],
        "OR": [
            i.strip() + " County"
            for i in "Benton, Coos, Crook, Gilliam, Jackson, Jefferson, Josephine, Linn, Multnomah, Polk, Wasco, Yamhill".split(
                ","
            )
        ],
        "SC": [
            i.strip() + " County"
            for i in "Berkeley, Beaufort, Allendale, Chesterfield, Cherokee, Hampton, Kershaw".split(
                ","
            )
        ],
    }

    false_county_dict = {
        "CA": ["San Francisco County"],
        "CO": ["Denver County"],
        "ME": ["Franklin County", "Sagadahoc County"],
        "MT": ["Deer Lodge County", "Silver Bow County"],
        "NM": ["Lincoln County"],
        "WA": ["Pierce County", "Snohomish County", "Whatcom County"],
    }

    df[has_elex_col] = False
    for state in full_states:
        df.loc[df["ST"] == state, has_elex_col] = True

    for state in true_county_dict:
        df.loc[
            (df["ST"] == state) & (df["CTYNAME"].isin(true_county_dict[state])),
            has_elex_col,
        ] = True

    for state in false_county_dict:
        df.loc[
            (df["ST"] == state) & (df["CTYNAME"].isin(false_county_dict[state])),
            has_elex_col,
        ] = False

    return df

    pass


def has_2022_elex():
    df = county_populations()
    # source: https://theappeal.org/political-report/when-are-elections-for-prosecutor-and-sheriff/

    full_states = [
        "AL",
        "CA",
        "CO",
        "IL",
        "IN",
        "KY",
        "ME",
        "MD",
        "MI",
        "MA",
        "MN",
        "MT",
        "NE",
        "NV",
        "NH",
        "NM",
        "NC",
        "SD",
        "TN",
        "UT",
        "WA",
        "WI",
        "WY",
    ]

    # SD --> Every county "with an election is on the midterm cycle" ??

    true_county_dict = {
        "DE": ["Sussex County", "New Castle County"],
        "NJ": [
            i.strip() + " County"
            for i in "Burlington, Hudson, Hunterdon, Middlesex, Monmouth, Morris, Ocean, Passaic, Somerset, Sussex, Warren".split(
                ","
            )
        ],
        "NY": [
            i.strip() + " County"
            for i in "Allegany, Broome, Cayuga, Chautauqua, Clinton, Delaware, Essex, Franklin, Jefferson, Montgomery, Oneida, Onondaga, Ontario, Orange, Oswego, Otsego, Tompkins, Ulster".split(
                ","
            )
        ],
        "OR": [
            i.strip() + " County"
            for i in "Benton, Coos, Crook, Gilliam, Jackson, Jefferson, Josephine, Linn, Multnomah, Polk, Wasco, Yamhill".split(
                ","
            )
        ],
        "SC": [
            i.strip() + " County"
            for i in "Berkeley, Beaufort, Allendale, Chesterfield, Cherokee, Hampton, Kershaw".split(
                ","
            )
        ],
    }

    false_county_dict = {
        "CA": ["San Francisco County"],
        "CO": ["Denver County"],
        "ME": ["Franklin County", "Sagadahoc County"],
        "MT": ["Deer Lodge County", "Silver Bow County"],
        "NM": ["Lincoln County"],
        "WA": ["Pierce County", "Snohomish County", "Whatcom County"],
    }

    df["has_election_2022"] = False
    for state in full_states:
        df.loc[df["ST"] == state, "has_election_2022"] = True

    for state in true_county_dict:
        df.loc[
            (df["ST"] == state) & (df["CTYNAME"].isin(true_county_dict[state])),
            "has_election_2022",
        ] = True

    for state in false_county_dict:
        df.loc[
            (df["ST"] == state) & (df["CTYNAME"].isin(false_county_dict[state])),
            "has_election_2022",
        ] = False

    return df