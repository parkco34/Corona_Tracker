#!/usr/bin/env python
from textwrap import dedent
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

def replace_columns(prev_df, updated_df, updated_column=""):
    """ Repalce certain columns I know need to be replaced, whenever they pop up during the loop """
    if 'Case-Fatality_Ratio' in updated_df.columns:
        updated_df.rename(columns={'Case-Fatality_Ratio': 'Case_Fatality_Ratio'}, inplace=True)

    if 'Incident_Rate' in updated_df.columns:
        updated_df.rename(columns={'Incident_Rate': 'Incidence_Rate'}, inplace=True)

    """ Compare column headers, replacing ones that closely match the columns
    of the new dataframe with the old column headers """
    if len(prev_df.columns) < len(updated_df.columns):
        for new_col in updated_df.columns:

            for old_col in prev_df.columns:
                seq = difflib.SequenceMatcher(None, old_col, new_col).ratio() * 100

                if new_col in prev_df.columns:
                    continue

                if seq >= 54:
                    updated_column = re.sub(old_col, new_col, old_col)
                    prev_df.rename(columns={old_col: updated_column}, inplace=True)

    """ Once the altered column headers have replaced the old ones, find
    location of missing column headers and insert them accordingly  """
    if len(prev_df.columns) != len(updated_df.columns):
        for idx, col in enumerate(updated_df.columns):

            if col not in prev_df.columns:
                prev_df.insert(idx, column=col, value="")
#                print("New column: " + col + "\nAt index: " + str(idx))

def missing_values(dataframe):
    for typ in dataframe.columns:
        if dataframe[typ].isnull().any():
            if (dataframe[typ].dtype == 'int') or (dataframe[typ].dtype == 'float'):
                dataframe[typ] = dataframe[typ].fillna(0)
            elif (dataframe[typ].dtype == 'object'):
                dataframe[typ] = dataframe[typ].fillna('')

    return dataframe

def get_state_data(df, state, local=False):
    df = df.loc[df['Confirmed'] != 0]

    # Change below because local is being returned with nothing in it!
    if local:
        local = df.loc[(df['Admin2'] == 'Livingston') | (df['Admin2'] == 'Monroe') & (df['Province_State'] == state)]
        data = local[['Confirmed', 'Deaths', 'Recovered', 'Combined_Key']]

        _ = data.plot(figsize=(16, 5), subplots=False, title=state + ' ' + 'Rona')
        _ = plt.xlabel('Date')
        _ = plt.ylabel('Infected')

        if not os.path.exists('/Users/whitney/rona_graphs/'):
            os.makedirs('/Users/whitney/rona_graphs/')
            auto.alert(text='Created rona_graphs directory...', title='HEADS '\
                'UP!', button='Understood?')
            plt.savefig(r"{}".format("/Users/whitney/rona_graphs/" + todaystr + '_' + state + '_UpstateNY'))

        else:
            plt.savefig(r"{}".format("/Users/whitney/rona_graphs/" + todaystr + '_' + state + '_UpstateNY'))

    else:
        df = df.loc[df['Province_State'] == state]
        data = df[['Confirmed', 'Deaths', 'Recovered', 'Combined_Key']]

        _ = data.plot(figsize=(16, 5), subplots=False, title=state + ' ' + 'Rona')
        _ = plt.xlabel('Date')
        _ = plt.ylabel('Infected')


    return data


def get_dates(start_date, final_date):
    dates = pd.date_range(start_date, final_date, freq="d")
    dates = dates.strftime("%m-%d-%Y")
    dates = dates.tolist()
    return dates

def gui_wannabe(
    start_date=input(
        dedent(
            """
            Enter starting date in the form of: ("01-22-1990")\n
            """
        )
    ), 
final_date=input(
    dedent(
        """
        Enter a final date in the form of: ("06-08-1985")\n
        """
    )
)):
    return get_dates(start_date, final_date)

def scrape(website, path_to_click):
    
    driver = select_webdriver(False, True)   # Driver uses Chrome since, driver=True and is headless
#    driver = webdriver.Firefox(options=options)
#    breakpoint()
    driver.get(website)
    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
    waiting = WebDriverWait(driver, 17, ignored_exceptions=ignored_exceptions)

#    df = pd.DataFrame([], columns=new_columns)
    df = pd.DataFrame([])
    # Replace this with a GUI
    for dt in gui_wannabe():
# MAIN PART
#==============================================================
        try:
            waiting.until(EC.element_to_be_clickable((By.XPATH, '//*[@title="{}.csv"]'.format(dt)))).click()
            time.sleep(1.2)
            # Makes the element that is not visible, visible so it can click where it needs to
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

#        except TimeoutException as ex:
#            print("xpath: Something is going wrong at {}:".format(dt) + str(ex))

        except StaleElementReferenceException as err:
            print(f"Error: {err} \n==>@ {dt}")

        time.sleep(1.2)
        raw = waiting.until(EC.element_to_be_clickable((By.XPATH, '/html/body/pre'))).text
        raw_data = StringIO(raw)
        print(raw_data)

    # Scraping done, and now for Data Wrangling! =====================
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
        driver.back()
        time.sleep(.5)
        driver.back()
        time.sleep(.5)
#==============================================================

    return df
    
rona = scrape("https://github.com/CSSEGISandData/COVID-19", '//*[@id="raw-url"]')
#driver = select_webdriver(True, False)
#rona['Last_Update'] = pd.to_datetime(rona['Last_Update']).dt.date
#rona = rona.set_index('Last_Update')
# Obtains New York's Local Data to the Livonia/Rochester region
##ny = get_state_data(rona, 'New York', local=True)




