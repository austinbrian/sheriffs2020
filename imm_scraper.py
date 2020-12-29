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

"""
class ImmScraper():
    def __init__(self):
        self.url_to_scrape = "http://trac.syr.edu/phptools/immigration/detain/"
        self.page_items=[]
        self.all_items=[]
    # headless driver
    def start_driver(self):
        print('starting driver...')
        self.driver = webdriver.Firefox()
    def close_driver(self):
        print('closing driver...')
        self.driver.quit()
        self('closed!')
    def get_page(self,url):
        def get_page(self,url):
            print('getting page...')
            self.driver.get(url)
            sleep(randint(.5,1))
    def click_page
"""


def startup():
    url = "http://trac.syr.edu/phptools/immigration/detain/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")  # , from_encoding="utf-8")

    driver = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver")
    driver.get(url)
    print(driver.title)
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
    sleep(5)
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


def select_col_dropdown(driver, val="State", col=1):
    div = driver.find_element_by_id(f"col{col}head2")
    dropdown = Select(div.find_element_by_id("dimension_pick_col1"))
    options = dropdown.options
    opt_vals = [i.text for i in options]
    if val in opt_vals:
        options[opt_vals.index(val)].click()
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


def new_main(driver, DEBUG=False):
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

    for state in reversed(all_states):
        state_text = " ".join(state.text.split()[:-1])
        print(state_text)
        state.find_element_by_tag_name("a").click()
        sleep(0.5)
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
            print(f"Wrote {len(state_df)} records for {state_text}")
    tot_df = pd.DataFrame.from_records(
        records, columns="State,Facility,Year-Month,Total".split(",")
    )
    print(tot_df.shape)
    print(tot_df.head())
    if not DEBUG:
        state_total_df.to_csv("data/state_totals.csv", headers=False)
        tot_df.to_csv("data/total_county_facility_date.csv", headers=False)

    pass


if __name__ == "__main__":
    driver = startup()

    # old_main()

    # get all the county-facility numbers for each month-year
    new_main(driver, DEBUG=False)

    driver.close()
