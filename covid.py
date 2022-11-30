#!/usr/bin/env python
# Corona Tracker Web Scraper
"""
Corona Virus Tracker:
    Web scrapes the John Hopkins Whiting School of Engineering github
    site for covid data.
"""
from timeout_exceptions import *
from textwrap import dedent
import requests
import time
import os.path
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
DIRECTORY = "./raw_data/"
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
press = soup.find("a", {"title": "archived_data"})

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

csv_files = {
    1:
    # XPATH to .csv files
    # Need to get a more general way to reference the items on this page so I
    # can loop thru the given dates
    "/html/body/div[4]/div/main/turbo-frame/div/div/div[3]/div[4]/div/div[4]/div[2]/span/a",

}

def get_max_date(path):
    current_dir = os.getcwd()
    os.chdir(path)  # Change current directory 
    # Finds the latest file in the directory and returns it
    # Probably won't work on Windows machines, tho

    # Finds the latest file in the directory and returns it
    # If the grabbed directory doesn't match the filename format in the
    # destination directory, call user for directory name
    """
    Need to check that this works correctly
    """
    file = max(os.listdir(), key=os.path.getctime)

    if re.search(r"(\d+_\d+_\d+)", file):
        new_file = file.replace('_', '-')[:10]
        print(f"\nSuccess!\n{new_file}\n")
        os.chdir(current_dir)   # Change current directory back
        return max(os.listdir(), key=os.path.getctime).replace('_', '-')[:10]

    else:
        print(f"\nNo match dude: {file}\n")
        _path = input("\nEnter correct path:\n")
        os.chdir(_path)

        file = max(listdir(), key=os.path.getctime)
        if re.search(r"(\d+_\d+_\d+)", file):
            new_file = file.replace('_', '-')[:10]
            print(f"\nSuccess!\n{new_file}\n")
            os.chdir(current_dir)   # Change current directory back
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
    Determines the Webdriver to use depending the user's choice of browser, and
    the OPTIONS that are asserted.
    (*Currently for only FireFox and Chrome browsers*)
    -------------------------------------------------------------
    INPUTS:
        _thedriver: (bool) Selects Webdriver 
            (Default: False for Firefox Browser)
            (*Radio Button to choose BROWSER*)
            (Default: True for Chrome)
        _headless: (bool) Whether or not to EXLCUDE the BROWSER
            (Default: True)

    OUTPUTS:
        driver: (selenium.webdriver.(Firefox/Chrome).webdriver.WebDrvier) 
    -------------------------------------------------------------
    """

    if _thedriver:
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        options = Options()
        options.add_argument("start-maximized")

        if _headless:
            options.headless = True
            assert options.headless

        else:
            options.headless = False

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    else:
        from selenium.webdriver import Firefox
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        from webdriver_manager.firefox import GeckoDriverManager

        options = Options()
        options.add_argument("start-maximized")

        if _headless:
            options.headless = True
            assert options.headless

        else:
            options.headless = False
        
        # Obtains GeckoDriver from where ever it's located
        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    return driver

def what_to_press(path, how=False, _time=7, press=True):
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
    # Copies the text
    return WebDriverWait(driver,
                         _time).until(EC.presence_of_element_located((By.XPATH,
                                                                     element))).text

def data_grabber(date_list):
    """
    Iterates thru the given list of dates and writes them to txt file in
    specified directory, while to navigating depending on whether some data is
    trucnated
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
            what_to_press('//*[@title="{}.csv"]'.format(day))

        except TimeoutException as ex:

            # If file in question is truncated, use input field
            if not truncated:
                what_to_press("a.d-md-block", how=True)
                truncated = True
                time.sleep(1.075) 

            time.sleep(.75)
            # Input element:
            i = driver.find_element(By.CSS_SELECTOR, "#tree-finder-field")
            time.sleep(.5)
            i.send_keys(day)    # Enters date in search feild 
            time.sleep(1.1)
            what_to_press(
                dedent("""li.css-truncate:nth-child(2) > a:nth-child(1) >
                marked-text:nth-child(3)"""), 
                how=True)   # Clicks search result to properly dated file
            time.sleep(1.2)
            what_to_press('//*[@id="raw-url"]') # Clicks raw data button
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

    
# Driver uses Chrome since, driver=False and is headless
driver = select_webdriver(False, True)
# Function to prevent Selenium from running into timeout exception issues:
timeout_exceptions(driver, URL)

#except TimeoutException as ex:
#    print("\nSome shit happened with getting the webdriver or something\n")
#
PATH = "/Users/whitney/raw_data" # Directory for data storage (TEMPORARY)
# Datetime stuff:
today = date.today()
yesterday = today - timedelta(days=1)
yesterday = yesterday.strftime('%m-%d-%Y')
_datez = datez.Grab_Dates(get_max_date(PATH), yesterday)   # Generalizse this

what_to_press(xpaths[2], how=True)
time.sleep(1.5)
what_to_press(xpaths[3], how=True)
time.sleep(1.5) 

try:
    data_grabber(_datez.main())

except TimeoutException as ex:
    print("\nᕕ( ཀ ʖ̯ ཀ)ᕗ\n{ex}\n_datez.main()")

finally:
   driver.close()

