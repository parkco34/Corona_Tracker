#!/usr/bin/env python
# Borrowed from: https://shallowsky.com/blog/programming/selenium-timeouts.html
from urllib3.exceptions import MaxRetryError, NewConnectionError
from selenium.common.exceptions import TimeoutException
import sys
""" 
function to handle the timeout exceptions from Selenium 
while working with python to scrape webpages
"""

num_timeouts = 0
MAX_TIMEOUTS = 3

def timeout_exceptions(_driver, url):
    global num_timeouts

    if num_timeouts >= MAX_TIMEOUTS:
        return timeout_boilerplate(url, "I have given up the will to live\n")

    try:
        _driver.get(url)
        
    except TimeoutException as ex:
        num_timeouts += 1
        print(f"Shit! Timeout Exception! at \n{ex}\n", file=sys.stderr)

    except (ConnectionRefusedError, MaxRetryError, NewConnectionError) as e:
            # MaxRetryError and NewConnectionError come from urllib3.exceptions
            # ConnectionRefusedError is a Python builtin.
            num_timeouts += 1
            print("EEK! Connection error", e, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

    except Exception as e:
        num_timeouts += 1
        print("EEK! Unexpected exception in _driver.get: " + str(e))

    try:
        fullhtml = _driver.page_source

    except Exception as e:
        num_timeouts += 1
        print("EEK! Fetched page but couldn't get html: " + str(e))
