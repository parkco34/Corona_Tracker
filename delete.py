from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# set the options to use the Vivaldi browser
options = Options()
options.binary_location = '/path/to/vivaldi' # replace with the actual path to the Vivaldi executable

# setup the webdriver
webdriver_service = Service(ChromeDriverManager().install())

# create the driver
driver = webdriver.Chrome(service=webdriver_service, options=options)

# go to a website
driver.get("http://www.google.com")

# quit the driver
driver.quit()
