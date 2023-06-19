#!/usr/bin/env python
# Corona Tracker Web Scraper
# ========== PLAN ===========================
#    Data Scraper Object:
    #    Properties: website url, data source, location
    #    Methods: scrape data, clean data, store data
#    Data Storage Object:
    #    Properties: database name, table name, data format
    #    Methods: create database, create table, insert data, retrieve data
#    Data Analysis Object:
    #    Properties: location, time period, data type
    #    Methods: filter data, aggregate data, visualize data
#    Graphical Output Object:
#    Properties: chart type, color scheme, title
#    Methods: create chart, save chart, display chart
# =====================================
"""
Corona Virus Tracker:
    Web scrapes the John Hopkins Whiting School of Engineering github
    site for covid data.
"""
import re
import Grab_Dates as datez
import difflib
from io import StringIO
import matplotlib.pyplot as plt
import Scrape as scrape
from datetime import date, timedelta, datetime
import pandas

"""Add a function to look at latest text file created and start from that
date.
Otherwise, have user enter the inital start date
"""

"""
--------------------------------------------------------------------------------------------
GET GECKODRIVER for automatic installation so user doesn't have to worry about
it!
--------------------------------------------------------------------------------------------
"""

class Corona(object):
    # Dictionary of xpaths and other strings to for web scraping
    xpaths = {
        # XPATH:
        1:"/html/body/div[5]/div/main/turbo-frame/div/div/div/div[3]/div[1]/div[2]/div[3]/div[1]/div[3]/div[2]/span/a",
         #CSS SELECTORS:
        2: """div.Box-row:nth-child(3) > div:nth-child(2) > span:nth-child(1) >
        a:nth-child(1)""",
        3: "div.Box-row:nth-child(3) > div:nth-child(2) > span:nth-child(1) > a:nth-child(1)",
        4: "/html/body/div[5]/div/main/turbo-frame/div/div/div[1]/div[4]/a",
    }

    def __init__(self, url: str, driver):
        self.url = url
        self.driver = None
    

    def get_max_date(path):
        os.chdir(path)  # Change current directory 
        # Finds the latest file in the directory and returns it
        # Probably won't work on Windows machines, tho

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

    # Deals with missing values
    def missing_values(dataframe):
        for typ in dataframe.columns:
            if dataframe[typ].isnull().any():
                if (dataframe[typ].dtype == 'int') or (dataframe[typ].dtype == 'float'):
                    dataframe[typ] = dataframe[typ].fillna(0)
                elif (dataframe[typ].dtype == 'object'):
                    dataframe[typ] = dataframe[typ].fillna('')

        return dataframe


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


