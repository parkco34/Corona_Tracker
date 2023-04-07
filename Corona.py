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
import Scrape as scrape
from datetime import date, timedelta, datetime
import pandas

"""Add a function to look at latest text file created and start from that
date.
Otherwise, have user enter the inital start date
"""

"""
--------------------------------------------------
GET GECKODRIVER for automatic installation so user doesn't have to worry about
it!
--------------------------------------------------
"""

class Corona(object):
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

    def __init__(self, url: str, driver):
        self.url = url
        self.driver = None
    

    def get_max_date(path):
        os.chdir(path)  # Change current directory 
        # Finds the latest file in the directory and returns it
        # Probably won't work on Windows machines, tho

        # Finds the latest file in the directory and returns it
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

# ==============================
rona = Corona("https://github.com/CSSEGISandData/COVID-19")
print(rona)



