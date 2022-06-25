#!/usr/bin/env python
import MyMod as 
import difflib
import os
import re
import smtplib
import ssl
import time
from io import StringIO
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import numpy as np
import csv
import pyautogui as auto
import matplotlib.pyplot as plt


thedriver=True, # OOPS
__headless=True
    # Check if chromedriver is used
    # Need to have something in place for when User doesn't have a driver
    # installed already..
    if thedriver:
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
        driver = webdriver.Chrome(executable_path=DRIVE,
                                       options=options)

    else:
#            from selenium.webdriver import Firefox
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        from webdriver_manager.firefox import GeckoDriverManager

        options = Options()
        options.add_argument("start-maximized")

        if __headless:
            options.headless = True
            assert options.headless

        else:
            options.headless = False
        
        # Obtains GeckoDriver from where ever it's located
        DRIVE = mymod.find_file('geckodriver 2')
        driver = webdriver.Firefox(executable_path=DRIVE, options=options)
