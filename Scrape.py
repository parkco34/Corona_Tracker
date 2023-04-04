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



