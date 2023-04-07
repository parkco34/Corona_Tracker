#!/usr/bin/env python
# Scrape class for Web Scraping
from timeout_exceptions import *
from textwrap import dedent
import time
import os.path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

class Scrape(object):

    def __init__(self, url, tags) -> None:
        self.attributes = {'url': url, 'tags': tags}
        
    def select_webdriver(
        _thedriver=False,
        _headless=True,
    ):
        """
        determines the webdriver to use depending the user's choice of browser, and
        the options that are asserted.
        (*currently for only firefox and chrome browsers*)
        -------------------------------------------------------------
        inputs:
            _thedriver: (bool) selects webdriver 
                (default: false for firefox browser)
                (*radio button to choose browser*)
                (default: true for chrome)
            _headless: (bool) whether or not to exlcude the browser
                (default: true)

        outputs:
            driver: (selenium.webdriver.(firefox/chrome).webdriver.webdrvier) 
        -------------------------------------------------------------
        """

        if _thedriver:
            from selenium.webdriver.chrome.options import options
            from selenium.webdriver.chrome.service import service
            from webdriver_manager.chrome import chromedrivermanager
            options = options()
            options.add_argument("start-maximized")

            if _headless:
                options.headless = true
                assert options.headless

            else:
                options.headless = false

            driver = webdriver.chrome(service=service(chromedrivermanager().install()), options=options)

        else:
            from selenium.webdriver import firefox
            from selenium.webdriver.firefox.options import options
            from selenium.webdriver.firefox.service import service
            from webdriver_manager.firefox import geckodrivermanager

            options = options()
            options.add_argument("start-maximized")

            if _headless:
                options.headless = true
                assert options.headless

            else:
                options.headless = false
            
            # obtains geckodriver from where ever it's located
            driver = webdriver.firefox(service=service(geckodrivermanager().install()), options=options)

        return driver

    def what_to_press(path, how=False, _time=7, press=True):
        """
        INPUT:
            path: (str) path to element
            how: (bool, default: False) Determines the way you locate the element
            _time: (int) Time to wait for element to be visible

        OUPUT:
            None
        """
        if how:
            element = WebDriverWait(driver,
                                    _time).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                               path))) 
    #        print(f"\nFOUND IT! {str(element)}\n")  # Incase something happens, I
            # know where to look on the webpage
        else:
            element = WebDriverWait(driver,
                                    _time).until(EC.presence_of_element_located((By.XPATH,
                                                                               path))) 
        if press:
            element.click()


    def scraper(element, directory="./raw_data2", filetype=".txt", _time=7):
        # Copies the text
        return WebDriverWait(driver,
                             _time).until(EC.presence_of_element_located((By.XPATH,
                                                                         element))).text

    def scraper(element, directory="./raw_dataz", filetype=".txt", _time=7):
        # Get directory user wishes to save scraped data to, if at all
        filepath = none
        save_files = true
        while(save_files):
            print("do you wanna save scraped data to a directory?")
            if (save_files):
                print("enter the path for the directory")
                filepath = input("")
        # Copies the text
        return WebDriverWait(driver,
                             _time).until(EC.presence_of_element_located((By.XPATH, path))) 


# ====================================================================
