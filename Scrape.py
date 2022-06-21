#!/usr/bin/env python
import Old_Get_Dates as when
import Old_MyModule as mymod
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

class Scrape(object):

    def __init__(
        self,
        URL,
        __driver,
        __headless=True
    ):
        self.URL = URL
        self.driver = driver
