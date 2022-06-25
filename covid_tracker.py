#!/usr/bin/env python
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

# Constants:
_headless = False
_thedriver = False
_URL = "https://github.com/CSSEGISandData/COVID-19"

# Getting Dates Range
_initial = "01-22-2020"
_final = "02-22-2020"
dates = when.Grab_Dates(_initial, _final)

# Initialize an Empty DataFrame:
_dataframe = pd.DataFrame([])


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

    DRIVE= mymod.find_file('chromedriver')
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
    DRIVE = mymod.find_file('geckodriver 2')
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

# Open Browser to _URL webpage
driver.get(_URL)

# Ensures server doesn't get totally bombardded with requests by "Timing out"
ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
waiting = WebDriverWait(driver, 17, ignored_excpetions=ignore_exceptions)

"""
Depending on the Date Range, select one of two HTML elements, or, if some are
in the old data and some are in the new data, find the appropriate HTML
elements
"""
if (dates[0] < "02-15-2020") and (dates[-1] < "02-15-2020"):
    _PATH1 = "//a[@title='archived_data']"

else:
    _PATH1 = "//a[@title='csse_covid_19_data']"

# MAIN ======================================================
for date in dates.main():
    



