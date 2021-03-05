import sys

sys.path.append("..")
from imm_scraper import *


def set_up_state_county_agency(driver):
    select_col_dropdown(driver, "County/Surrounding Area", col=1)
    sleep(0.2)
    select_col_dropdown(driver, "Fiscal Year", col=2)
    sleep(0.2)
    select_col_dropdown(driver, "Apprehension Method/Agency", col=3)
    sleep(0.2)


def get_years_in_county(driver, county):

    df = pd.DataFrame()
    return df


def convert_county_year_to_row(county, year, tups):

    tups.insert(0, ("County/Surrounding Area", county))
    tups.insert(1, ("Fiscal Year", year))
    ind, lst = list(zip(*tups))

    return pd.DataFrame(pd.Series(lst, index=ind).T)


if __name__ == "__main__":

    driver = startup(reason="arrest")
    already_scraped = []
    try:
        df = pd.read_csv("data/arrest_data.csv")
        already_scraped = df["County/Surrounding Area"].unique()
    except FileNotFoundError:
        df = pd.DataFrame()
        print("df created")
    set_up_state_county_agency(driver)
    counties = get_all_options_in_column(driver, col=1)
    counties = list(filter(remove_all, counties))
    counties = list(filter(lambda x: x not in already_scraped, counties))
    for county in counties:
        make_selection_in_col(driver, county, col=1)
        sleep(0.5)
        years = get_all_options_in_column(driver, col=2)
        years = sorted(list(filter(remove_all, years)))
        for year in years:
            make_selection_in_col(driver, year, col=2)
            sleep(0.5)
            tups = capture_items_in_table(driver, col=3)
            row = convert_county_year_to_row(county, year, tups)
            df = pd.concat([df, row.T], axis=0).fillna(0)
            sleep(0.2)
        df.drop_duplicates().to_csv("data/arrest_data.csv", index=False)
        rowtotal = len(df)
        print(f"Completed {county} -- {rowtotal} total rows")
        if len(df) % 50 == 0:
            driver.close()

            sleep(0.1)
            driver = startup(reason="arrest")
            set_up_state_county_agency(driver)

    driver.quit()
