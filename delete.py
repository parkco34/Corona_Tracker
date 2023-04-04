#!/usr/bin/env python
"""
Here's a Python program using Selenium that checks the current GeckoDriver version, and installs the latest version if the installed version is out of date
--------------------------------------
To use this script, just change the GECKODRIVER_PATH VARIABLE to the path where your GeckoDriver is installed, and run the script.
"""
import requests
from selenium import webdriver

# Define the URL to fetch the latest version of GeckoDriver
url = 'https://github.com/mozilla/geckodriver/releases/latest'

# Fetch the latest version number
response = requests.get(url)
latest_version = response.url.split('/')[-1]

# Define the path to the installed GeckoDriver
geckodriver_path = '/usr/local/bin/geckodriver' # Change this to your own path

# Check the current version of GeckoDriver
browser_version = webdriver.Firefox(executable_path=geckodriver_path).capabilities['browserVersion']
current_version = '.'.join(browser_version.split('.')[:3])

# Compare the current version with the latest version
if current_version != latest_version:
    # Download the latest version of GeckoDriver
    download_url = f'https://github.com/mozilla/geckodriver/releases/download/{latest_version}/geckodriver-{latest_version}-macos.tar.gz'
    response = requests.get(download_url)

    # Save the downloaded file to disk
    with open('geckodriver.tar.gz', 'wb') as f:
        f.write(response.content)

    # Extract the downloaded file
    import tarfile
    with tarfile.open('geckodriver.tar.gz', 'r:gz') as tar:
        tar.extractall()

    # Move the extracted file to the correct path
    import os
    os.replace(f'geckodriver', geckodriver_path)

    print(f'Updated GeckoDriver from {current_version} to {latest_version}')
else:
    print(f'GeckoDriver is up-to-date at version {current_version}')


