#!/usr/bin/env python
#"""
#Here's a Python program using Selenium that checks the current GeckoDriver version, and installs the latest version if the installed version is out of date
#--------------------------------------
#To use this script, just change the GECKODRIVER_PATH VARIABLE to the path where your GeckoDriver is installed, and run the script.
#"""
#import requests
#from selenium import webdriver
#
## Define the URL to fetch the latest version of GeckoDriver
#url = 'https://github.com/mozilla/geckodriver/releases/latest'
#
## Fetch the latest version number
#response = requests.get(url)
#latest_version = response.url.split('/')[-1]
#
## Define the path to the installed GeckoDriver
#geckodriver_path = '/usr/local/bin/geckodriver' # Change this to your own path
#
## Check the current version of GeckoDriver
#browser_version = webdriver.Firefox(executable_path=geckodriver_path).capabilities['browserVersion']
#current_version = '.'.join(browser_version.split('.')[:3])
#
## Compare the current version with the latest version
#if current_version != latest_version:
#    # Download the latest version of GeckoDriver
#    download_url = f'https://github.com/mozilla/geckodriver/releases/download/{latest_version}/geckodriver-{latest_version}-macos.tar.gz'
#    response = requests.get(download_url)
#
#    # Save the downloaded file to disk
#    with open('geckodriver.tar.gz', 'wb') as f:
#        f.write(response.content)
#
#    # Extract the downloaded file
#    import tarfile
#    with tarfile.open('geckodriver.tar.gz', 'r:gz') as tar:
#        tar.extractall()
#
#    # Move the extracted file to the correct path
#    import os
#    os.replace(f'geckodriver', geckodriver_path)
#
#    print(f'Updated GeckoDriver from {current_version} to {latest_version}')
#else:
#    print(f'GeckoDriver is up-to-date at version {current_version}')
#
#
class Scrape(object):
    def __init__(self, url, xpaths:list) -> None:
        self.attributes = {'url': url, 'xpaths': xpaths}
        self.driver = None

    def select_webdriver(
        self,
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

            # obtains geckodriver from where ever it's located
            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

        self.driver = driver
        return driver

    @staticmethod
    def scraper(driver, path, _time=7):
        # Copies the text
        return WebDriverWait(driver,
                             _time).until(EC.presence_of_element_located((By.XPATH,
                                                                          path)))

    def what_to_press(self, path, how=False, _time=7, press=True):
        """
        INPUT:
            path: path to element
            how: (bool, default: False) Determines the way you locate the element
            _time: (int) Time to wait for element to be visible

        OUPUT:
            None
        """
        if how:
            element = WebDriverWait(self.driver,
                                    _time).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                self.scraper(self.driver, path))))

        else:
            element = WebDriverWait(self.driver,
                                    _time).until(EC.presence_of_element_located((By.XPATH,
                                                                               path)))

        if press:
            element.click()

        return None

