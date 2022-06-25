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
_PATH = '/html/body/pre'
_PATH1 = "//a[@title='archived_data']"
_PATH2 = "//a[@title='archived_daily_case_updates']"
_PATH3 = "//a[@title='csse_covid_19_data']"
_initial = "01-22-2020"
_final = "02-22-2020"
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

def get_raw_data(_PATH: str) -> pd.DataFrame:
        
        raw = waiting.until(EC.element_to_be_clickable((By.XPATH, _PATH))).text
        raw_data = StringIO(raw)

        if dt != start_date:
            df2 = pd.read_csv(raw_data)
            df2 = missing_values(df2)
            replace_columns(df, df2)

            if 'Last_Update' in df2.columns:
                df2['Last_Update'] = pd.to_datetime(df2['Last_Update'])

            elif 'Last Update' in df2.columns:
                df2['Last Update'] = pd.to_datetime(df2['Last Update'])

            try:
                df = pd.concat([df, df2], axis=0, ignore_index=True)
            except Exception as err:
                print(f"Error: \n{err}")

        else:
            df1 = pd.read_csv(raw_data)
            df1 = missing_values(df1)

            try:
                if 'Last Update' in df1.columns:
                    df1['Last Update'] = pd.to_datetime(df1['Last Update'])

                elif 'Last_Update' in df1.columns:
                    df1['Last_Update'] = pd.to_datetime(df1['Last_Update'])

            except Exception as err:
                print(f"Error occurred! => {err}")

            df = pd.concat([df, df1], axis=0, ignore_index=True)

        time.sleep(.5)
        self.driver.back()
        time.sleep(.5)
        self.driver.back()
        time.sleep(.5)

        return df

breakpoint()
scrape = sc.Old_Scrape(_URL, False, False)
_dataframe = get_raw_data(_PATH)
scrape.the_scraping(_PATH1, get_raw_data(_PATH), _initial, _final)



