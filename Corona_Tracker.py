#!/usr/bin/env python
import Old_Scrape as sc
import difflib
import os
import re
import smtplib
import ssl
import time
from io import StringIO
import pandas as pd


"""
Time Series Analysis on Covid infections, deaths and recoveries via the CDC's
Data with ability to specify LOCATION with visualization 
"""

_URL = "https://github.com/CSSEGISandData/COVID-19"
_PATH1 = "//a[@title='archived_data']"
_PATH2 = "/a[@title='archived_daily_case_updates']"
#_data1, _data2 = _DATA_PATHS1
## If a LIST is returned, use other function to scrape raw data and
## concatenate... using a for loop .. JUST KIDDING THAT WONT WORK
## SHOULD BE ABLE TO STORE THE CACHE SOMEWHERE AND USE THAT FOR EFFICIENCY
#_data1.click()
#
#_raw_btn = driver.find_element(By.XPATH, "//a[@id='raw-url']")
#_raw_text= waiting.until(EC.element_to_be_clickable((By.XPATH, '/html/body/pre'))).text
#raw_data = StringIO(_raw_text)
#
#driver.back()
#driver.back()
#
## After next iteration through _DATA_PATHS1:
#_data2.click()

scrape = sc.Old_Scrape(_URL, False)

ignored_exceptions = (sc.NoSuchElementException, sc.StaleElementReferenceException)
thewaiting = sc.WebDriverWait(sc.drive, 17, ignored_exceptions=ignored_exceptions)

breakpoint()
