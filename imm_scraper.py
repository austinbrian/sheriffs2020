#!bin/bash/python
import pandas as pd
import requests
import lxml.html
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep
from random import randint
import datetime
import warnings


def startup(reason="detain"):
    url = f"http://trac.syr.edu/phptools/immigration/{reason}/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")  # , from_encoding="utf-8")

    driver = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver")
    driver.get(url)
    # print(driver.title)
    html = driver.page_source
    html = BeautifulSoup(html, "lxml")
    # sleep(6)
    return driver


def scrape_details(driver):
    """This identifies the current things that are clicked on and returns them as a dict"""
    ice_dict = {}
    # Get state and jurisdiction selected by click in the table
    state_xpath = "//div[@id='col1']/table/tbody/tr[@class='rowsel']/td/a"
    jurisdiction_xpath = "//div[@id='col2']/table/tbody/tr[@class='rowsel']/td/a"
    ice_dict["State"] = driver.find_element_by_xpath(state_xpath).text
    ice_dict["Jurisdiction"] = driver.find_element_by_xpath(jurisdiction_xpath).text

    # Break apart the county and facility to roll up sheriffs
    if " - " in ice_dict["Jurisdiction"]:
        ice_dict["County"] = ice_dict["Jurisdiction"].split(" - ")[0]
        ice_dict["Facility"] = ice_dict["Jurisdiction"].split(" - ")[1]
    else:
        ice_dict["County"] = ice_dict["Jurisdiction"]
        ice_dict["Facility"] = ice_dict["Jurisdiction"]

    # Get the money table, "yes" means ICE took custody of detainee
    for i in range(
        len(driver.find_elements_by_xpath('//*[@id="col3"]/table/tbody/tr/td')) / 2
    ):
        # this is in a loop because this xpath returns full table of elements, sometimes 4, sometimes 6
        # here we ask it for each of
        label_xpath = '//*[@id="col3"]/table/tbody/tr[{}]/td[1]'.format(i + 1)
        num_xpath = '//*[@id="col3"]/table/tbody/tr[{}]/td[2]'.format(i + 1)
        label = driver.find_element_by_xpath(label_xpath).text
        num = driver.find_element_by_xpath(num_xpath).text
        ice_dict[label] = num
    return ice_dict


def get_jurisdictions(driver):
    """Gets the scraped info calling prior function for each jurisdiction, and returns df"""
    df = pd.DataFrame(
        columns=["State", "Jurisdiction", "All", "Yes", "No", "County", "Facility"]
    )
    success_counter = 0
    failure_counter = 0
    # sleep(5)
    for i in driver.find_elements_by_xpath("//div[@id='col2']/table/tbody/tr/td/a"):
        i.click()  # click on it
        sleep(0.5)  # just to make sure the page gets a chance to load
        try:
            x = scrape_details()  # collect the info
            df.loc[len(df)] = pd.DataFrame(x, index=[0]).loc[0]  # add it to the df
            success_counter += 1
        except:
            print(i.text, "failed")
            failure_counter += 1
            pass
    print("{} succeeded".format(success_counter))
    print("{} failed".format(failure_counter))
    print("----------------")
    return df


def old_main(driver):
    all_jur_xpath = '//*[@id="col1"]/table/tbody/tr[1]/td/a'  # want to exclude this
    all_state_xpath_template = '//*[@id="col1"]/table/tbody/tr[{}]/td/a'
    # Run the script
    full_nation_df = pd.DataFrame(
        columns=["State", "Jurisdiction", "All", "Yes", "No", "County", "Facility"]
    )
    for state in range(2, 58):  # starts at 2 because element #1 is "all"
        a = driver.find_element_by_xpath(all_state_xpath_template.format(state))
        state_name = a.text
        print(state_name)
        a.click()
        state_df = get_jurisdictions()
        state_df.to_csv(
            "./state_files/{}_ice_detainees.csv".format(state_name), index=False
        )  # why not save each state?
        full_nation_df = full_nation_df.append(state_df, ignore_index=True)

    # format datetime
    def get_year_date():
        month = time.strftime("%b")
        day = time.strftime("%d")
        year = time.strftime("%Y")
        datestring = "{}-{}-{}".format(day, month, year)
        return datestring

    datestring = get_year_date()
    full_nation_df.to_csv("./data/ice_detainees_{}.csv".format(datestring), index=False)
    driver.quit()


def select_col_dropdown(driver, val="State", col=1, verbose=False):
    div = driver.find_element_by_id(f"col{col}head2")
    dropdown = Select(div.find_element_by_id("dimension_pick_col1"))
    options = dropdown.options
    opt_vals = [i.text for i in options]
    if val in opt_vals:
        options[opt_vals.index(val)].click()
        if verbose:
            print("Selected", val)
    else:
        pass


def capture_header(driver, col=1):
    header = div.find_element_by_tag_name("thead")
    # all these headers are the col name and " Total" so parse that total
    hed_text_list = [header.text[: header.text.index(" Total")], "Total"]
    return hed_text_list


def capture_items_in_table(driver, col=1):
    div = driver.find_element_by_id(f"col{col}")

    # drop all the key/vals into a dict
    rows = div.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")
    tb = list()
    for r in rows:
        vals = r.find_elements_by_tag_name("td")
        key, val = [i.text for i in vals]
        # val = r.find_element_by_tag_name("td").text
        # val = r.find_element_by_class_name("Data r").text
        # tb[key] = val
        tb.append((key, val))

    return tb


def click_each_selection_in_table(driver, col=1):
    div = driver.find_element_by_id(f"col{col}")


def get_totals_all_states(driver, DEBUG=False):
    t0 = datetime.datetime.now()
    # first get the county-facility numbers for every state
    select_col_dropdown(driver, val="State", col=1)
    sleep(0.5)
    select_col_dropdown(driver, val="County-Facility Detainer Sent", col=2)
    sleep(0.5)
    select_col_dropdown(driver, val="Month and Year", col=3)
    sleep(0.5)
    state_totals = capture_items_in_table(driver, col=1)
    cf_vals = capture_items_in_table(driver, col=2)
    state_total_df = pd.DataFrame.from_records(state_totals, columns=["State", "Total"])
    cf_total_df = pd.DataFrame.from_records(
        cf_vals, columns=["County-Facility Detainer Sent", "Total"]
    )

    # recall we changed the dropdown to state above
    all_states = (
        driver.find_element_by_id("col1")
        .find_element_by_tag_name("tbody")
        .find_elements_by_tag_name("tr")
    )

    if DEBUG:
        all_states = all_states[-3:]

    records = []

    for state in all_states[1:6]:
        state_text = " ".join(state.text.split()[:-1])
        print(state_text)
        state.find_element_by_tag_name("a").click()
        sleep(2)
        date_pairs = capture_items_in_table(driver, col=3)
        facilities_in_state = (
            driver.find_element_by_id("col2")
            .find_element_by_tag_name("tbody")
            .find_elements_by_tag_name("tr")
        )
        for facility in facilities_in_state:
            facility_text = " ".join(facility.text.split()[:-1])
            print(facility_text)
            facility.find_element_by_tag_name("a").click()
            sleep(2)
            facility_date_pairs = capture_items_in_table(driver, col=3)
            for z in facility_date_pairs:
                x, y = z
                records.append((state_text, facility_text, x, y))
        if not DEBUG:
            state_df = pd.DataFrame.from_records(
                records, columns="State,Facility,Year-Month,Total".split(",")
            )
            state_df.to_csv(f"data/state_total_{state_text}.csv")
            timeval = datetime.datetime.now() - t0
            print(
                f"Wrote {len(state_df)} records for {state_text} in {timeval.seconds//60} total minutes"
            )
    tot_df = pd.DataFrame.from_records(
        records, columns="State,Facility,Year-Month,Total".split(",")
    )
    print(tot_df.shape)
    print(tot_df.head())
    if not DEBUG:
        state_total_df.to_csv("data/state_totals.csv", headers=False)
        tot_df.to_csv("data/total_county_facility_date.csv", headers=False)

    pass


def remove_all(l):
    """removes any entry from a list of tuples that includes "All"
    Intended to be used with a filter function"""
    for x in l:
        if x == "All":
            return False
        else:
            return True


def make_selection_in_col(driver, selection, col=1):
    div = driver.find_element_by_id(f"col{col}")
    sleep(0.2)
    div.find_element_by_link_text(selection).click()
    sleep(0.1)


def set_up_facility_date(driver):
    select_col_dropdown(driver, val="County-Facility Detainer Sent", col=1)
    sleep(1)

    select_col_dropdown(driver, val="Month and Year", col=2)
    sleep(1)


def set_up_facility_year(driver):
    select_col_dropdown(driver, val="County-Facility Detainer Sent", col=1)
    sleep(1)

    select_col_dropdown(driver, val="Fiscal Year", col=2)
    sleep(1)


def get_details_for_facility_date(driver):
    """Get all the dropdown details for a single facility-date comparison."""
    d = dict()
    for entry in [
        # "Month and Year",
        "Fiscal Year",
        "County-Facility Detainer Sent",
        "State",
        "Facility Type",
        "ICE Assumed Custody After Detainer Issued",
        "Notice (Not Detainer) Issued",
        "Detainer Refused",
        "Most Serious Criminal Conviction (MSCC)",
        "Seriousness Level of MSCC Conviction",
        "Criminal History",
        "Age Group",
        "Citizenship",
        "Gender",
    ]:
        select_col_dropdown(driver, val=entry, col=3)
        sleep(0.2)
        tups = capture_items_in_table(driver, col=3)
        d[entry] = list(filter(remove_all, tups))
        sleep(0.2)
    return d


def get_all_options_in_column(driver, col=1):
    div = driver.find_element_by_id(f"col{col}")
    table = div.find_element_by_tag_name("tbody")
    full_list = [
        i.find_element_by_tag_name("a").text
        for i in table.find_elements_by_tag_name("tr")
    ]
    return list(filter(lambda x: x != "All", full_list))


def check_total(num, ref, *args):
    """Check that the number is the same as the reference.
    If it's not, print something to that effect.
    """
    if int(ref.replace(",", "")) != int(num.replace(",", "")):
        warnings.warn(f"{args}The current value {num} should be {ref}")
        return False
    else:
        return True


def convert_data_to_tups(d):
    data = d.copy()
    try:
        facility, facility_total = data["County-Facility Detainer Sent"][0]
    except Exception as e:
        print(e)
        print(data)
    kv_tups = [("Total Detainers", facility_total)]
    gender = data.get("Gender", [])
    data.pop("Gender")
    citizenship = data.get("Citizenship", [])
    data.pop("Citizenship")
    date = data.get("Month and Year", data.get("Fiscal Year", []))

    categorical_vars = [
        "County-Facility Detainer Sent",
        "Fiscal Year",
        # "Month and Year",
        "State",
        "Facility Type",
    ]

    for i in categorical_vars:
        data[i] = data[i][0]
        if check_total(data[i][1], facility_total, facility, i):
            kv_tups.append((i, data[i][0]))
            data.pop(i)
        else:
            f = open("data/weird_jurisdictions.txt", "a")
            f.write(f"{facility};{i};{date}\n")
            f.close()
            data.pop(i)
            continue

    for i in data.keys():
        for a in data[i]:
            entry, val = a
            concat_name = "-".join([i, entry])
            kv_tups.append((concat_name, val))
    for i in gender:
        kv_tups.append(i)
    for i in citizenship:
        kv_tups.append(i)

    return kv_tups


def get_2021_counties():
    """Source:"""
    kansas = ["Wyandotte"]
    louisiana = ["Orleans"]
    ny = "Chenango, Cattaraugus, Chemung, Columbia, Erie, Livingston, Madison, Monroe, Putnam, Saratoga, Schenectady, Schoharie, Schuyler, Suffolk, Wayne, Wyoming".split(
        ", "
    )
    nj = "Bergen, Camden, Essex, Gloucester, Salem".split(", ")
    penn = "Adams, Allegheny, Armstrong, Blair, Bucks, Butler, Cambria, Cameron, Clarion, Clearfield, Columbia, Cumberland, Delaware, Erie, Forest, Greene, Huntingdon, Juniata, Lackawanna, Lawrence, Lebanon, Lycoming, McKean, Mifflin, Perry, Pike, Schuylkill, Susquehanna, Tioga, Union, Venango, Washington".split(
        ", "
    )
    # Each of 38 independent cities elect a sheriff on their gubernatorial cycle (the year after the presidential election: 2017, and so on).
    virginia = ['Alexandria city', 'Bristol city', 'Buena Vista city', 'Charlottesville city', 'Chesapeake city', 'Colonial Heights city', 'Covington city', 'Danville city', 'Emporia city', 'Fairfax city', 'Falls Church city', 'Franklin city', 'Fredericksburg city', 'Galax city', 'Hampton city', 'Harrisonburg city', 'Hopewell city', 'Lexington city', 'Lynchburg city', 'Manassas city', 'Manassas Park city', 'Martinsville city', 'Newport News city', 'Norfolk city', 'Norton city', 'Petersburg city', 'Poquoson city', 'Portsmouth city', 'Radford city', 'Richmond city', 'Roanoke city', 'Salem city', 'Staunton city', 'Suffolk city', 'Virginia Beach city', 'Waynesboro city', 'Williamsburg city', 'Winchester city']

    state_county_dict = dict(
        zip(
            [
                "Kansas",
                "Louisiana",
                "New York",
                "New Jersey",
                "Pennsylvania",
                "Virginia",
            ],
            [kansas, louisiana, ny, nj, penn, virginia],
        )
    )
    return state_county_dict


def get_facilities_in_state_county(driver, state, county):

    # select each state and get the corresponding set of county-facility detainers
    select_col_dropdown(driver, "State", col=1)
    sleep(0.2)
    select_col_dropdown(driver, "County-Facility Detainer Sent", col=2)
    sleep(2)
    make_selection_in_col(driver, state, col=1)
    all_facility_names = get_all_options_in_column(driver, col=2)

    return [i for i in all_facility_names if county.lower() in i.lower()]


def get_facilities_in_listed_counties(driver, state, *counties):
    # select each state and get the corresponding set of county-facility detainers
    select_col_dropdown(driver, "State", col=1)
    sleep(0.2)
    select_col_dropdown(driver, "County-Facility Detainer Sent", col=2)
    sleep(1)
    make_selection_in_col(driver, state, col=1)
    sleep(1)
    all_facility_names = get_all_options_in_column(driver, col=2)
    if not counties:
        counties = get_2021_counties()[state]
    list_to_send = []
    for c in counties:
        for f in all_facility_names:
            if c.lower() in f.lower():
                list_to_send.append(f)

    return list_to_send


def scrape_detainers(driver):
    set_up_facility_date(driver)
    t0 = datetime.datetime.now()
    all_facilities_to_parse = get_all_options_in_column(driver, col=1)
    # Add in 2021 elections to parse those first
    # virginia = get_facilities_in_state_county(driver, "Virginia", "city")
    # ny = get_facilities_in_listed_counties(driver, "New York")
    # nj = get_facilities_in_listed_counties(driver, "New Jersey")
    # ks = get_facilities_in_listed_counties(driver, "Kansas")
    # lou = get_facilities_in_listed_counties(driver, "Louisiana")
    # penn = get_facilities_in_listed_counties(driver, "Pennsylvania")

    # all_facilities_to_parse = (
    #     virginia + ks + ny + nj + lou + penn + sorted(all_facilities_to_parse)
    # )

    df = pd.DataFrame(pd.read_csv("data/total_yearly_data.csv"))
    number_currently_in_file = df["County-Facility Detainer Sent"].nunique()
    facilities_already_scraped = df["County-Facility Detainer Sent"].unique()
    all_facilities_to_parse = list(
        filter(lambda x: x not in facilities_already_scraped, all_facilities_to_parse)
    )
    set_up_facility_year(driver)
    print(f"This session will parse {len(all_facilities_to_parse)} facilities")
    for facility in all_facilities_to_parse:
        make_selection_in_col(driver, facility, col=1)
        sleep(0.2)
        all_dates_to_parse = get_all_options_in_column(driver, col=2)

        # Limit to the 48 most recent months for which there is data, or 8 years
        for date in sorted(all_dates_to_parse, reverse=True)[:8]:
            try:
                make_selection_in_col(driver, date, col=2)
                sleep(0.2)
                d = get_details_for_facility_date(driver)
                ind, lst = list(zip(*convert_data_to_tups(d)))
                row = pd.DataFrame(pd.Series(lst, index=ind))
                df = pd.concat([df, row.T], axis=0).fillna(0)
                make_selection_in_col(driver, facility, col=1)
            except Exception as e:
                print(e, "--", facility, date)
                continue
        # df.to_csv("data/total_data.csv", index=False)
        df.to_csv("data/total_yearly_data.csv", index=False)
        rowtotal = len(df)

        t1 = datetime.datetime.now()
        tval = t1 - t0
        print(
            f"Completed {facility} - {len(df)} total rows in {tval.seconds//60} minutes"
        )

        if len(df) % 10 == 0:
            driver.close()

            sleep(0.1)
            driver = startup()
        set_up_facility_year(driver)
        t0 = datetime.datetime.now()


if __name__ == "__main__":
    driver = startup(reason="detain")

    # old_main()

    # get all the county-facility numbers for each month-year
    scrape_detainers(driver)

    driver.close()
