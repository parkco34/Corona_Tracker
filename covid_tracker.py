#!/usr/bin/env python3
import difflib
import os
import re
import smtplib
import ssl
import time
from datetime import date, timedelta, datetime
#from email.mime.image import MIMEImage
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from io import StringIO
import numpy as np
import csv
import pyautogui as auto
import matplotlib.pyplot as plt
import pandas as pd
from selenium import webdriver
import Old_MyModule as mymod
import Grab_Dates as when

# Constants/Private variables:
_headless = False
_thedriver = False
_URL = "https://github.com/CSSEGISandData/COVID-19"
_PATH2 = "//a[@title='csse_covid_19_daily_reports']"
path_to_click = '//*[@id="raw-url"]'

# Getting Dates Range
_initial = "02-22-2020"
_final = "06-08-2020"
dates = when.Grab_Dates(_initial, _final)
dates = dates.main()

# Initialize an Empty DataFrame:
df = pd.DataFrame([])


# Scraping:

if _thedriver:
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    options = Options()
    options.add_argument("start-maximized")

    if __headless:
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

#breakpoint()

# Open Browser to _URL webpage
driver.get(_URL)

# Ensures server doesn't get totally bombardded with requests by "Timing out"
ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
waiting = WebDriverWait(driver, 17, ignored_exceptions=ignored_exceptions)

_threshold_date_for_directory_loc="02-15-2020"
"""
Depending on the Date Range, select one of two HTML elements, or, if some are
in the old data and some are in the new data, find the appropriate HTML
elements
"""
if (dates[-1] < _threshold_date_for_directory_loc):
    _PATH1 = "//a[@title='archived_data']"

    elem = driver.find_element(By.XPATH, _PATH1)
    elem.click()
    elem = driver.find_element(By.XPATH, _PATH2)
    elem.click()

else:
    _PATH1 = "//a[@title='csse_covid_19_data']"

    elem = driver.find_element(By.XPATH, _PATH1)
    elem.click()
    elem = driver.find_element(By.XPATH, _PATH2)
    elem.click()


for date in dates:
    try:

        waiting.until(EC.element_to_be_clickable((By.XPATH,\
            '//*[@title="{}.csv"]'.format(date)))).click()

        time.sleep(1.2)

        for _ in range(0, 5):
            try:

                ActionChains(driver).move_to_element(driver.find_element(By.XPATH, path_to_click)).click(driver.find_element(By.XPATH, path_to_click))
                waiting.until(EC.element_to_be_clickable((By.XPATH, path_to_click))).click()

                str_error = None
                # Why do I ge the error at all??
            except NoSuchElementException:
                str_error = 'MESSAGE!'

            if str_error:
                time.sleep(2)
                print('\n\nstr_error = ' + str_error)
            else:
                break

    except TimeoutException as ex:
        print("xpath: Something is going wrong at {}:".format(date) + str(ex))

    except StaleElementReferenceException as err:
        print(f"Error: {err} \n==>@ {date}")

    time.sleep(1.2)

    # Raw Data
    raw = waiting.until(EC.element_to_be_clickable((By.XPATH, '/html/body/pre'))).text

#    raw_data = StringIO(raw)

    """
    ++++++++++++++++++++++++++++++++++
    Save Raw Data in another directory
    Should take user input
    ++++++++++++++++++++++++++++++++++
    """
    with open(f"./raw_data/raw_data_file{date}.txt", "w") as file:
        file.write(raw)

    time.sleep(.5)
    driver.back()
    time.sleep(.5)
    driver.back()
    time.sleep(.5)

# Data Wrangling ====================================================
#    if date != _initial:
#        df2 = pd.read_csv(raw_data)
#        df2 = missing_values(df2)
#        replace_columns(df, df2)
#
#        if 'Last_Update' in df2.columns:
#            df2['Last_Update'] = pd.to_datetime(df2['Last_Update'])
#
#        elif 'Last Update' in df2.columns:
#            df2['Last Update'] = pd.to_datetime(df2['Last Update'])
#
#        try:
#            df = pd.concat([df, df2], axis=0, ignore_index=True)
#        except Exception as err:
#            print(f"Error: \n{err}")
#
#    else:
#        df1 = pd.read_csv(raw_data)
#        df1 = missing_values(df1)
#
#        try:
#            if 'Last Update' in df1.columns:
#                df1['Last Update'] = pd.to_datetime(df1['Last Update'])
#
#            elif 'Last_Update' in df1.columns:
#                df1['Last_Update'] = pd.to_datetime(df1['Last_Update'])
#
#        except Exception as err:
#            print(f"Error occurred! => {err}")
#
#        df = pd.concat([df, df1], axis=0, ignore_index=True)
#
#    time.sleep(.5)
#    driver.back()
#    time.sleep(.5)
#    driver.back()
#    time.sleep(.5)
#


