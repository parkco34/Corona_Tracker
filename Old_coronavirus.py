#!/usr/bin/env python3
# This needs to be refactored... BADLY
# Also needs Chrome Driver installed for web scraping.
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
from io import StringIO
import matplotlib.pyplot as plt
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

# ====================GET DATES===============================
final_date = '03-22-2020'
start_date = '02-22-2020'
today = date.today()
todaystr = today.strftime('%m-%d-%Y')
#yesterday = today - timedelta(days=1)
#yesterday = yesterday.strftime('%m-%d-%Y')


def get_dates(start_date, final_date):
    date_i = datetime.strptime(start_date, '%m-%d-%Y')
#    dates = pd.date_range(date_i, today - timedelta(days=1), freq='d')
#     dates = pd.date_range(start_date, yesterday, freq='d')
    # Earlier Dates
    dates = pd.date_range(start_date, final_date, freq='d')
    dates = dates.strftime('%m-%d-%Y')
    dates = dates.tolist()
    return dates

# =======================================================

# ============ DEAL w/ MISSING VALUES ====================

def missing_values(dataframe):
    for typ in dataframe.columns:
        if dataframe[typ].isnull().any():
            if (dataframe[typ].dtype == 'int') or (dataframe[typ].dtype == 'float'):
                dataframe[typ] = dataframe[typ].fillna(0)
            elif (dataframe[typ].dtype == 'object'):
                dataframe[typ] = dataframe[typ].fillna('')

    return dataframe


# =======================================================

# ============= MANAGING VARIATIONS IN COLUMN NAMES =====

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
            if col not in prev_df.columns:
                prev_df.insert(idx, column=col, value="")
#                print("New column: " + col + "\nAt index: " + str(idx))

# =======================================================

# ============ OBTAINING DATA DEPENDING ON STATE =========

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
            plt.savefig(r"{}".format("/Users/whitney/rona_graphs/" + todaystr + '_' + state + '_UpstateNY'))

        else:
            plt.savefig(r"{}".format("/Users/whitney/rona_graphs/" + todaystr + '_' + state + '_UpstateNY'))

    else:
        df = df.loc[df['Province_State'] == state]
        data = df[['Confirmed', 'Deaths', 'Recovered', 'Combined_Key']]

        _ = data.plot(figsize=(16, 5), subplots=False, title=state + ' ' + 'Rona')
        _ = plt.xlabel('Date')
        _ = plt.ylabel('Infected')

        plt.savefig(r'{}'.format("../rona_graphs/" + todaystr + '_' + state))

    return data

# =======================================================

# I need a function that will do this for me: If a column is added to raw data I'm scraping,
# add the new column and branch off to create new data frame and continue concatenating data

# ====================== SELENIUM STUFF ==================

ff_driver = "webdrivers/geckodriver 2"
site = "https://github.com/CSSEGISandData/COVID-19"
options = FirefoxOptions()
options.add_argument("--start-maximized")
options.headless = False
#assert options.headless

# =======================================================

# =======================================================

#def consolidate_columns(new_dframe, old_dframe):
#    # Getting both dataframe columns as lists and extracting the missing columns and their indices
#    oldcol_list = list(old_dframe.columns)
#    newcol_list = list(new_dframe.columns)
#    # Difference between lists or arrays, where assume_unique=True prevents the function from sorting the values
#    missing_list = np.setdiff1d(newcol_list, oldcol_list, assume_unique=True).tolist()
#
#    for i in missing_list:
#        # Gets index of the missing column names
#        j = new_dframe.columns.get_loc(i)
#        old_dframe.insert(j, i, "")

# =======================================================

# ============== MAIN EVENT: WEB SCRAPER ==================

def scrape(path_to_click):
    driver = webdriver.Firefox(executable_path=ff_driver, options=options)
#    driver = webdriver.Firefox(options=options)
#    breakpoint()
    driver.get(site)
#    breakpoint()
    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
    waiting = WebDriverWait(driver, 17, ignored_exceptions=ignored_exceptions)

#    df = pd.DataFrame([], columns=new_columns)
    df = pd.DataFrame([])

    for dt in get_dates(start_date, final_date):
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

        except TimeoutException as ex:
            print("xpath: Something is going wrong at {}:".format(dt) + str(ex))

        except StaleElementReferenceException as err:
            print(f"Error: {err} \n==>@ {dt}")

        time.sleep(1.2)
        raw = waiting.until(EC.element_to_be_clickable((By.XPATH, '/html/body/pre'))).text
        raw_data = StringIO(raw)

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

# =======================================================

rona = scrape('//*[@id="raw-url"]')
# Set datetime index:
#breakpoint()
rona['Last_Update'] = pd.to_datetime(rona['Last_Update']).dt.date
rona = rona.set_index('Last_Update')

# Get old dataframe
#df_i = pd.read_csv(r'C:\Users\cparker\Desktop\Python\rona_05-13-2021.csv')

# Update the columns for our new data
#consolidate_columns(rona, df_i)

# }}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
#rona = pd.concat([df_i, rona], axis=0, ignore_index=True)
#rona.to_csv(r'../rona_graphs/rona_{}.csv'.format(final_date))
# }}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}

#
#rona['Last_Update'] = pd.to_datetime(rona['Last_Update']).dt.date
#rona = rona.set_index('Last_Update')

# Get State Data:
# =============================================================================
ny = get_state_data(rona, 'New York', local=True)
ca = get_state_data(rona, 'California')
tx = get_state_data(rona, 'Texas')
az = get_state_data(rona, 'Arizona')
wash = get_state_data(rona, 'Washington')
wash = get_state_data(rona, 'Washington')
wash = get_state_data(rona, 'Washington')
florida = get_state_data(rona, 'Florida')
all_ny = get_state_data(rona, 'New York')
# =============================================================================
# Send Email: /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
#
#
#def send_it(state, sender_email, send_to):
#
#    message = MIMEMultipart('alternative')
#    message['Subject'] = '! Corona Virus Update !'
#    message['From'] = sender_email
#    message['To'] = ", ".join(send_to)
#
#    text = """\
#        Hello friend,
#        This is an automatic email sent to you through my python script!!"""
#
#    html = """\
#        <html>
#            <body>
#                <p>Hello friend,<br>
#                    Here's a link to the current global corona virus status:
#                    <a href="https://www.worldometers.info/coronavirus/">Corona Virus Info</a>
#                    <br>
#                    <hr>
#                </p>
#                <img src="https://media.giphy.com/media/Lq7TFOIexfjgkCsupk/giphy.gif" alt="gif failed to be shown">
#            </body>
#        </html>"""
#
#    # Turn these into plain/html MIMEText objects
#    part1 = MIMEText(text, 'plain')
#    part2 = MIMEText(html, 'html')
#    # The email client will try to render the last part first:
#    message.attach(part1)
#    message.attach(part2)
#
#    # DataFrame:
#    get_state_data(rona, state)
#
#    img = open(r'{}.png'.format(todaystr + '_' + state), 'rb')
#    msg_image = MIMEImage(img.read())
#    img.close()
#    msg_image.add_header('Content-ID', '<image1>')
#
#    doc = open(r'thou_shalt_pass.txt')
#    password = doc.readline()
#    password = password[:-1]
#    doc.close()
#    context = ssl.create_default_context()
#    with smtplib.SMTP_SSL('smtp.gmail.com', port=port, context=context) as server:
#        server.login(sender_email, password)
#        server.sendmail(sender_email, send_to, message.as_string())
#
#send_it('New York', 'parkercorya@yahoo.com', 'cparker@hahnauto.com')
#
#
#
