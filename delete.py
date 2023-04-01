#!/usr/bin/env python
import requests
import os
from zipfile import ZipFile

gecko_url = 'https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-v0.30.0-win64.zip'
chrome_url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'

def download_driver(url, driver_name):
    print(f"Downloading {driver_name} driver...")
    response = requests.get(url)
    with open(f"{driver_name}.zip", "wb") as file:
        file.write(response.content)
    print(f"Extracting {driver_name} driver...")
    with ZipFile(f"{driver_name}.zip", "r") as zip_ref:
        zip_ref.extractall(os.getcwd())
    os.remove(f"{driver_name}.zip")
    print(f"{driver_name} driver downloaded successfully")

def get_latest_chrome_version():
    response = requests.get(chrome_url)
    return response.text.strip()

def check_driver_version(driver_path, latest_version):
    version = os.popen(f"{driver_path} --version").read().strip()
    print(f"Current {os.path.basename(driver_path)} version: {version}")
    if version != latest_version:
        print(f"{os.path.basename(driver_path)} driver is outdated")
        download_driver(gecko_url if "gecko" in driver_path else chrome_url, os.path.basename(driver_path).replace(".exe", ""))
    else:
        print(f"{os.path.basename(driver_path)} driver is up-to-date")

def main():
    chrome_version = get_latest_chrome_version()
    check_driver_version("chromedriver.exe", chrome_version)
    check_driver_version("geckodriver.exe", "v0.30.0")

if __name__ == "__main__":
    main()


