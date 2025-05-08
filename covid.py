#!/usr/bin/env python
# Corona Tracker Web Scraper
"""
Corona Virus Tracker:
    Web scrapes the John Hopkins Whiting School of Engineering github
    site for covid data.
"""
import re
import pandas
from timeout_exceptions import *
import glob
from textwrap import dedent
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import Grab_Dates as datez
from datetime import date, timedelta, datetime

"""Add a function to look at latest text file created and start from that
date.
Otherwise, have user enter the inital start date
"""

URL = "https://github.com/CSSEGISandData/COVID-19"

"""
--------------------------------------------------
GET GECKODRIVER for automatic installation so user doesn't have to worry about
it!
--------------------------------------------------
"""

# Dictionary of xpaths and other strings to for web scraping
xpaths = {
    # XPATH:
    1:"/html/body/div[5]/div/main/turbo-frame/div/div/div/div[3]/div[1]/div[2]/div[3]/div[1]/div[3]/div[2]/span/a",
    # CSS SELECTORS:
    2: """div.Box-row:nth-child(3) > div:nth-child(2) > span:nth-child(1) >
    a:nth-child(1)""", 
    3: "div.Box-row:nth-child(3) > div:nth-child(2) > span:nth-child(1) > a:nth-child(1)",
    4: "/html/body/div[5]/div/main/turbo-frame/div/div/div[1]/div[4]/a",
}

def get_max_date(path):
    os.chdir(path)  # Change current directory 
    # Finds the latest file in the directory and returns it
    # Probably won't work on Windows machines, tho

    # Finds the latest file in the directory and returns it
    # If the grabbed directory doesn't match the filename format in the
    # destination directory, call user for directory name
    """
    Need to check that this works correctly *****
    """
    file = max(os.listdir(), key=os.path.getctime)

    if re.search(r"(\d+_\d+_\d+)", file):
        new_file = file.replace('_', '-')[:10]
        
#        print(f"\nSuccess!\n{new_file}\n")
        return max(os.listdir(), key=os.path.getctime).replace('_', '-')[:10]

    else:
        print(f"\nNo match dude: {file}\n")
        _path = input("\nEnter correct path:\n")
        os.chdir(_path)

        file = max(listdir(), key=os.path.getctime)
        if re.search(r"(\d+_\d+_\d+)", file):
            new_file = file.replace('_', '-')[:10]
            print(f"\nSuccess!\n{new_file}\n")
            return max(os.listdir(), key=os.path.getctime).replace('_', '-')[:10]


#    else:
#        return input(
#    """\nEnter the starting date in the format: mm-dd-yyyy\n
#    """) + ".txt"

def select_webdriver(
    _thedriver=False,
    _headless=True,
):
    """
    determines the webdriver to use depending the user's choice of browser, and
    the options that are asserted.
    (*currently for only firefox and chrome browsers*)
    -------------------------------------------------------------
    inputs:
        _thedriver: (bool) selects webdriver 
            (default: false for firefox browser)
            (*radio button to choose browser*)
            (default: true for chrome)
        _headless: (bool) whether or not to exlcude the browser
            (default: true)

    outputs:
        driver: (selenium.webdriver.(firefox/chrome).webdriver.webdrvier) 
    -------------------------------------------------------------
    """

    if _thedriver:
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import service
        from webdriver_manager.chrome import chromedrivermanager
        options = Options()
        options.add_argument("start-maximized")

        if _headless:
            options.headless = True
            assert options.headless

        else:
            options.headless = False

        driver = webdriver.chrome(service=service(chromedrivermanager().install()), options=options)

    else:
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager

        options = webdriver.FirefoxOptions()
        if _headless:
            options.add_argument('-headless')

        service = FirefoxService(executable_path=GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

    return driver

def what_to_press(driver, path, how=False, _time=7, press=True):
    """
    INPUT:
        path: (str) path to element
        how: (bool, default: False) Determines the way you locate the element
        _time: (int) Time to wait for element to be visible

    OUPUT:
        None
    """
    if how:
        element = WebDriverWait(driver,
                                _time).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                           path))) 
#        print(f"\nFOUND IT! {str(element)}\n")  # Incase something happens, I
        # know where to look on the webpage
    else:
        element = WebDriverWait(driver,
                                _time).until(EC.presence_of_element_located((By.XPATH,
                                                                           path))) 
    if press:
        element.click()


def scraper(element, directory="./raw_data2", filetype=".txt", _time=7):
    # Get directory user wishes to save scraped data to, if at all
    # Copies the text
    return WebDriverWait(driver,
                         _time).until(EC.presence_of_element_located((By.XPATH,
                                                                     element))).text

def data_grabber(date_list):
    """
    Iterates thru the given list of dates and writes them to txt file in
    specified directory while navigating, depending on whether some data is
    truncted
    ---------------------------------------------------------------------
    INPUTS:
        date_list: (list) List of dates from Grab_Dates class

    OUTPUTS:
        returns not a damn thing
    ---------------------------------------------------------------------
    """
    truncated = False   # Whether the file we're looking for is truncated
    for day in _datez.main():
        """
        Need to turn this into a function *********
        """
        time.sleep(.5)
        try:
            # Pressing  the link to the csv date
            what_to_press(driver, '//*[@title="{}.csv"]'.format(day))

        except TimeoutException as ex:

            # If file in question is truncated, use input field
            if not truncated:
                print("Truncated!")
                what_to_press(driver, "a.d-md-block", how=True)
                truncated = True
                time.sleep(1.075) 

            time.sleep(.75)
            # Input element:
            i = driver.find_element(By.CSS_SELECTOR, "#tree-finder-field")
            time.sleep(.5)
            i.send_keys(day)    # Enters date in search feild 
            time.sleep(1.1)
            what_to_press(driver,
                dedent("""li.css-truncate:nth-child(2) > a:nth-child(1) >
                marked-text:nth-child(3)"""), 
                how=True)   # Clicks search result to properly dated file
            time.sleep(1.2)
            what_to_press(driver, '//*[@id="raw-url"]') # Clicks raw data button
            time.sleep(1.2)
            
            # Store text files in raw_data directory
            with open(os.path.join(PATH, f"{day[:2]}_{day[3:5]}_{day[6:10]}.txt"),
                     "w") as file:  # w when file exists but empty
                txt = scraper(r"/html/body/pre")
                file.write(txt)
                
            # Previous page
            time.sleep(1.4)
            driver.back()
            time.sleep(1.5)
            driver.back()
            time.sleep(.5)


# ================================================================================
# Data Wrangling
#def data_wrangler(filepath):
#    file_list = glob.glob(path)
#    print(file_list
# ================================================================================

# Driver uses Chrome since, driver=False and is headless
driver = select_webdriver(False, True)
# Function to prevent Selenium from running into timeout exception issues:
timeout_exceptions(driver, URL)
PATH = "/Users/whitney/raw_data" # Directory for data storage (TEMPORARY)
# Datetime stuff:
today = date.today()
yesterday = today - timedelta(days=1)
yesterday = yesterday.strftime('%m-%d-%Y')

_datez = datez.Grab_Dates(get_max_date(PATH), yesterday)   # Generalizse this

what_to_press(driver, xpaths[2], how=True)
time.sleep(1.5)
what_to_press(driver, xpaths[3], how=True)
time.sleep(1.5) 

try:
    data_grabber(_datez.main())

except TimeoutException as ex:
    try:
        data_grabber(_datez.main())

    except TimeoutException as ex:
        print(f"\nᕕ( ཀ ʖ̯ ཀ)ᕗ\n{ex}\n_datez.main()")

finally:
   driver.close()

