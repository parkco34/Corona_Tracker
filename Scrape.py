#!/usr/bin/env python
# Scrape class for Web Scraping
from textwrap import dedent
import time # time.sleep()
import os.path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

class Scrape(object):

    def __init__(self, url, xpaths:list) -> None:
        self.attributes = {'url': url, 'xpaths': xpaths}
        
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
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import service
            options = Options()
            options.add_argument("start-maximized")

            if _headless:
                options.headless = True
                assert options.headless

            else:
                options.headless = False

            driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)


        else:
            from selenium.webdriver import firefox
            from selenium.webdriver.firefox.options import Options
            from selenium.webdriver.firefox.service import service
            from webdriver_manager.firefox import geckodrivermanager

            options = Options()
            options.add_argument("start-maximized")

            if _headless:
                options.headless = true
                assert options.headless

            else:
                options.headless = false
            
            # obtains geckodriver from where ever it's located
            driver = webdriver.firefox(service=service(geckodrivermanager().install()), options=options)

        return driver

    def what_to_press(path:str, how=False, _time=7, press=True):
        """
        INPUT:
            path: (str) path to element
            how: (bool, default: False) Determines the way you locate the element
            _time: (int) Time to wait for element to be visible

        OUPUT:
            None
        """
        if how:
            print("PATH --> " + str(type(path)))
            print("NEW PATH ==> " + str(path))
            element = WebDriverWait(driver,
                                    _time).until(EC.presence_of_element_located((By.CSS_SELECTOR,path))) 
    #        print(f"\nFOUND IT! {str(element)}\n")  # Incase something happens, I
            # know where to look on the webpage
        else:
            print(path)
            element = WebDriverWait(driver,
                                    _time).until(EC.presence_of_element_located((By.XPATH,
                                                                               path))) 

        if press:
            element.click()

        return str(path)

    def scraper(element, _time=7):
        # Copies the text
        return WebDriverWait(driver,
                             _time).until(EC.presence_of_element_located((By.XPATH, path))) 


# e===================================================================
scrape = Scrape("https://github.com/CSSEGISandData/COVID-19",
        ["/html/body/div[5]/div/main/turbo-frame/div/div/div/div[3]/div[1]/div[2]/div[3]/div[1]/div[3]/div[2]/span/a",
"""div.Box-row:nth-child(3) > div:nth-child(2) > span:nth-child(1) > a:nth-child(1)""",
"div.Box-row:nth-child(3) > div:nth-child(2) > span:nth-child(1) > a:nth-child(1)"])
driver = scrape.select_webdriver(_headless=False)
pathz = scrape.attributes["xpaths"][1]
scrape.what_to_press("/html/body/div[5]/div/main/turbo-frame/div/div/div/div[3]/div[1]/div[2]/div[3]/div[1]/div[3]/div[2]/span/a")
breakpoint()
