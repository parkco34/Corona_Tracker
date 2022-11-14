#!/usr/bin/env python
"""
Corona Virus Tracker:
    Web scrapes the John Hopkins Whiting School of Engineering github
    site for covid data.
"""
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
_datez = datez.Grab_Dates("01-22-2020", "03-22-2020")   # Generalizse this

URL = "https://github.com/CSSEGISandData/COVID-19"
DIRECTORY = "./raw_data/"
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
press = soup.find("a", {"title": "archived_data"})

# Dictionary of xpaths and other strings to for web scraping
xpaths = {
    # XPATH:
    1:"/html/body/div[5]/div/main/turbo-frame/div/div/div/div[3]/div[1]/div[2]/div[3]/div[1]/div[3]/div[2]/span/a",
    # CSS SELECTORS:
    2: """div.Box-row:nth-child(3) > div:nth-child(2) > span:nth-child(1) >
    a:nth-child(1)""", 
    3: "div.Box-row:nth-child(3) > div:nth-child(2) > span:nth-child(1) > a:nth-child(1)",
    4: "",
}

csv_files = {
    1:
    # XPATH to .csv files
    # Need to get a more general way to reference the items on this page so I
    # can loop thru the given dates
    "/html/body/div[4]/div/main/turbo-frame/div/div/div[3]/div[4]/div/div[4]/div[2]/span/a",

}


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

def what_to_press(path, how=False, _time=7):
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
    element.click()


def scraper(element, directory="./raw_data", filetype=".txt", _time=7):
    # Copies the text
    return WebDriverWait(driver,
                         _time).until(EC.presence_of_element_located((By.XPATH,
                                                                     element))).text

    
try:
    # Driver uses Chrome since, driver=False and is headless
    driver = select_webdriver(False, False)
    driver.set_page_load_timeout(1)
    driver.get(URL)

except TimeoutException as ex:
    print("\nSome shit happened with getting the webdriver or something\n")

PATH = "./raw_data" # Directory for data storage (TEMPORARY)
try:
    what_to_press(xpaths[2], how=True)
    time.sleep(1)
    what_to_press(xpaths[3], how=True)
    time.sleep(1) 

    for day in _datez.main():
        time.sleep(.5)
        # Pressing  the link to the csv date
        what_to_press('//*[@title="{}.csv"]'.format(day))
        time.sleep(.5)
        what_to_press('//*[@id="raw-url"]')
        time.sleep(.5)
        
        # Store text files in raw_data directory
        with open(os.path.join(PATH, f"{day[:2]}_{day[3:5]}_{day[6:10]}.txt"),
                 "w+") as file:
            txt = scraper(r"/html/body/pre")
            file.write(txt)
            
        # Previous page
        driver.back()
        driver.back()

except TimeoutException as ex:
    print("\nSome shit occured with locating the element.: " + str(ex) + "\n")

finally:
    driver.close()

