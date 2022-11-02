#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

URL = "https://github.com/CSSEGISandData/COVID-19"
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
press = soup.find("a", {"title": "archived_data"})


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


driver = select_webdriver(False, False)   # Driver uses Chrome since, driver=True and is headless
driver.get(URL)
ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
waiting = WebDriverWait(driver, 17, ignored_exceptions=ignored_exceptions)
waiting.until(EC.element_to_be_clickable((By.XPATH,
                                          '//*[@title="{}.csv"]'.format("01-20-2020")))).click()



