#!/usr/bin/env python
import Scrape as sc
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

scrape = sc.Scrape(_URL, False)
driver.get(_URL)

ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
waiting = WebDriverWait(driver, 17, ignored_exceptions=ignored_exceptions)

#ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
#waiting = WebDriverWait(driver, 17, ignored_exceptions=ignored_exceptions)
#_DATA_PATHS1 = driver.find_elements(By.PARTIAL_LINK_TEXT, f"{datez[0]}") 



breakpoint()
