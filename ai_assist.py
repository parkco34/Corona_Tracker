#!/usr/bin/env python
"""
COVID-19 Data Tracker
---------------------
This script scrapes COVID-19 data from the Johns Hopkins CSSE GitHub repository,
processes it, and generates visualizations.

The script is designed to be robust against website changes by using
more reliable selection methods and proper error handling.
"""

import os
import re
import time
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Dict, Union, Optional, Tuple

# Data processing
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException
)
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

# For automatic webdriver installation
try:
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    logging.warning("webdriver-manager not installed. You'll need to provide driver paths manually.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("covid_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("covid_tracker")

# Constants
GITHUB_URL = "https://github.com/CSSEGISandData/COVID-19"
DATA_DIR = Path("covid_data")
GRAPH_DIR = Path("covid_graphs")
DEFAULT_TIMEOUT = 10  # seconds


class CovidTracker:
    """Main class for tracking COVID-19 data"""

    def __init__(
        self,
        start_date: str = None,
        end_date: str = None,
        data_dir: Path = DATA_DIR,
        graph_dir: Path = GRAPH_DIR,
        browser: str = "firefox",
        headless: bool = True,
        driver_path: str = None,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Initialize the COVID tracker.

        Args:
            start_date: Start date in format 'MM-DD-YYYY' (defaults to last processed date or 30 days ago)
            end_date: End date in format 'MM-DD-YYYY' (defaults to yesterday)
            data_dir: Directory to store raw and processed data
            graph_dir: Directory to store generated graphs
            browser: Browser to use ('firefox' or 'chrome')
            headless: Whether to run browser in headless mode
            driver_path: Path to WebDriver executable (optional if webdriver-manager is installed)
            timeout: Default timeout for WebDriver operations in seconds
        """
        self.timeout = timeout

        # Setup directories
        self.data_dir = data_dir
        self.graph_dir = graph_dir
        self.data_dir.mkdir(exist_ok=True)
        self.graph_dir.mkdir(exist_ok=True)

        # Setup dates
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.yesterday_str = self.yesterday.strftime('%m-%d-%Y')

        if end_date:
            self.end_date = self._parse_date(end_date)
        else:
            self.end_date = self.yesterday

        if start_date:
            self.start_date = self._parse_date(start_date)
        else:
            # Try to find the last processed date or default to 30 days ago
            last_date = self._find_last_processed_date()
            if last_date:
                # Add one day to the last processed date to avoid duplication
                self.start_date = last_date + timedelta(days=1)
            else:
                self.start_date = self.end_date - timedelta(days=30)

        logger.info(f"Date range: {self.start_date.strftime('%m-%d-%Y')} to {self.end_date.strftime('%m-%d-%Y')}")

        # Initialize WebDriver
        self.browser = browser.lower()
        self.headless = headless
        self.driver_path = driver_path
        self.driver = None

        # Initialize data storage
        self.data = pd.DataFrame()

        # For debugging
        self.debug_mode = True
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)

    def _find_last_processed_date(self) -> Optional[date]:
        """Find the most recent date for which we have processed data"""
        try:
            csv_files = list(self.data_dir.glob("*.csv"))
            if not csv_files:
                return None

            latest_file = max(csv_files, key=os.path.getctime)
            # Extract date from filename using regex
            match = re.search(r'(\d{2}-\d{2}-\d{4})', latest_file.name)
            if match:
                date_str = match.group(1)
                return datetime.strptime(date_str, '%m-%d-%Y').date()
        except (ValueError, TypeError, FileNotFoundError) as e:
            logger.warning(f"Error finding last processed date: {e}")

        return None

    def _parse_date(self, date_str: str) -> date:
        """Parse date string in format MM-DD-YYYY"""
        try:
            return datetime.strptime(date_str, '%m-%d-%Y').date()
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Expected format: MM-DD-YYYY")

    def _init_webdriver(self):
        """Initialize the WebDriver based on browser choice"""
        if self.driver:
            return

        try:
            if self.browser == "firefox":
                options = FirefoxOptions()
                if self.headless:
                    options.add_argument('-headless')

                if WEBDRIVER_MANAGER_AVAILABLE and not self.driver_path:
                    service = FirefoxService(GeckoDriverManager().install())
                else:
                    service = FirefoxService(executable_path=self.driver_path)

                self.driver = webdriver.Firefox(service=service, options=options)

            elif self.browser == "chrome":
                options = ChromeOptions()
                options.add_argument("--start-maximized")
                if self.headless:
                    options.add_argument("--headless")

                if WEBDRIVER_MANAGER_AVAILABLE and not self.driver_path:
                    service = ChromeService(ChromeDriverManager().install())
                else:
                    service = ChromeService(executable_path=self.driver_path)

                self.driver = webdriver.Chrome(service=service, options=options)

            else:
                raise ValueError(f"Unsupported browser: {self.browser}. Use 'firefox' or 'chrome'.")

            self.driver.set_page_load_timeout(self.timeout)
            logger.info(f"Initialized {self.browser} WebDriver")

        except WebDriverException as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def _get_date_range(self) -> List[str]:
        """Get list of dates between start_date and end_date in format MM-DD-YYYY"""
        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        return [d.strftime('%m-%d-%Y') for d in date_range]

    def _wait_and_click(self, by: By, selector: str, timeout: int = None) -> bool:
        """Wait for element to be clickable and click it"""
        if timeout is None:
            timeout = self.timeout

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            element.click()
            return True
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            logger.warning(f"Failed to click element {selector}: {e}")
            return False

    def _wait_for_element(self, by: By, selector: str, timeout: int = None) -> Optional[webdriver.remote.webelement.WebElement]:
        """Wait for element to be present and return it"""
        if timeout is None:
            timeout = self.timeout

        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Element not found {selector}: {e}")
            return None

    def navigate_to_daily_reports(self):
        """Navigate to the daily reports folder in the GitHub repo using a more robust approach"""
        try:
            self.driver.get(GITHUB_URL)
            time.sleep(2)  # Allow page to fully load

            # Log the current page structure to help with debugging
            logger.info("Analyzing repository structure...")

            # First, try to find links by text content rather than attributes
            # Look for any link containing the text "csse_covid_19_data"
            csse_folder_clicked = False

            # Try multiple selector strategies
            selectors = [
                (By.XPATH, "//a[contains(text(), 'csse_covid_19_data')]"),
                (By.XPATH, "//a[contains(@href, 'csse_covid_19_data')]"),
                (By.XPATH, "//a[.//span[contains(text(), 'csse_covid_19_data')]]"),
                (By.XPATH, "//div[contains(@class, 'react-directory-filename-column')]//a[contains(., 'csse_covid_19_data')]"),
                (By.CSS_SELECTOR, "[data-testid='file-name-id-content']"),
                (By.CSS_SELECTOR, ".js-navigation-open"),
                (By.LINK_TEXT, "csse_covid_19_data")
            ]

            # Try each selector
            for by, selector in selectors:
                try:
                    # First, just try to find the element to see if it exists
                    elements = self.driver.find_elements(by, selector)
                    if elements:
                        logger.info(f"Found {len(elements)} potential elements with {by}:{selector}")
                        # Try to click the first element that contains the text we want
                        for element in elements:
                            try:
                                if "csse_covid_19_data" in element.text or "csse_covid_19_data" in element.get_attribute("href") or "csse_covid_19_data" in element.get_attribute("innerHTML"):
                                    logger.info(f"Found element with text: {element.text}")
                                    element.click()
                                    time.sleep(2)  # Wait for navigation
                                    csse_folder_clicked = True
                                    break
                            except:
                                continue
                        if csse_folder_clicked:
                            break
                except Exception as selector_error:
                    logger.warning(f"Selector {selector} failed: {selector_error}")
                    continue

            # If all selectors failed, try JavaScript click as a last resort
            if not csse_folder_clicked:
                try:
                    logger.info("Trying JavaScript click approach")
                    # Use JavaScript to find and click the link
                    self.driver.execute_script("""
                        var links = document.querySelectorAll('a');
                        for (var i = 0; i < links.length; i++) {
                            if (links[i].textContent.includes('csse_covid_19_data')) {
                                links[i].click();
                                return true;
                            }
                        }
                        return false;
                    """)
                    time.sleep(2)  # Wait for potential navigation

                    # Check if we navigated successfully
                    if "csse_covid_19_data" in self.driver.current_url:
                        csse_folder_clicked = True
                except Exception as js_error:
                    logger.warning(f"JavaScript click failed: {js_error}")

            if not csse_folder_clicked:
                # As a last resort, try to navigate directly to the expected URL
                try:
                    direct_url = f"{GITHUB_URL}/tree/master/csse_covid_19_data"
                    logger.info(f"Trying direct navigation to {direct_url}")
                    self.driver.get(direct_url)
                    time.sleep(2)
                    if "csse_covid_19_data" in self.driver.current_url:
                        csse_folder_clicked = True
                except Exception as direct_error:
                    logger.warning(f"Direct navigation failed: {direct_error}")

            if not csse_folder_clicked:
                raise Exception("Failed to navigate to csse_covid_19_data folder after trying multiple approaches")

            # Now navigate to the daily reports folder using the same robust approach
            daily_reports_clicked = False

            # Try the same selector strategies for daily reports
            for by, selector in selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    if elements:
                        for element in elements:
                            try:
                                if "csse_covid_19_daily_reports" in element.text or "csse_covid_19_daily_reports" in element.get_attribute("href") or "csse_covid_19_daily_reports" in element.get_attribute("innerHTML"):
                                    logger.info(f"Found daily reports element with text: {element.text}")
                                    element.click()
                                    time.sleep(2)  # Wait for navigation
                                    daily_reports_clicked = True
                                    break
                            except:
                                continue
                        if daily_reports_clicked:
                            break
                except Exception as selector_error:
                    logger.warning(f"Daily reports selector {selector} failed: {selector_error}")
                    continue

            # JavaScript approach for daily reports
            if not daily_reports_clicked:
                try:
                    self.driver.execute_script("""
                        var links = document.querySelectorAll('a');
                        for (var i = 0; i < links.length; i++) {
                            if (links[i].textContent.includes('csse_covid_19_daily_reports')) {
                                links[i].click();
                                return true;
                            }
                        }
                        return false;
                    """)
                    time.sleep(2)

                    if "csse_covid_19_daily_reports" in self.driver.current_url:
                        daily_reports_clicked = True
                except Exception as js_error:
                    logger.warning(f"JavaScript click failed for daily reports: {js_error}")

            # Direct URL approach for daily reports
            if not daily_reports_clicked:
                try:
                    direct_url = f"{GITHUB_URL}/tree/master/csse_covid_19_data/csse_covid_19_daily_reports"
                    logger.info(f"Trying direct navigation to {direct_url}")
                    self.driver.get(direct_url)
                    time.sleep(2)
                    if "csse_covid_19_daily_reports" in self.driver.current_url:
                        daily_reports_clicked = True
                except Exception as direct_error:
                    logger.warning(f"Direct navigation failed for daily reports: {direct_error}")

            if not daily_reports_clicked:
                raise Exception("Failed to navigate to csse_covid_19_daily_reports folder after trying multiple approaches")

            logger.info("Successfully navigated to daily reports folder")
            return True

        except Exception as e:
            logger.error(f"Failed to navigate to daily reports: {e}")
            # Take a screenshot to help with debugging
            try:
                screenshot_path = f"error_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Error screenshot saved to {screenshot_path}")
            except:
                pass
            return False

    def scrape_date(self, date_str: str) -> Optional[str]:
        """
        Scrape data for a specific date and return the raw CSV content.
        Uses a highly robust approach to handle changing GitHub UI.

        Args:
            date_str: Date in format MM-DD-YYYY

        Returns:
            Raw CSV content as string, or None if scraping failed
        """
        logger.info(f"Scraping data for {date_str}")

        # Check if we already have the file
        csv_path = self.data_dir / f"covid_{date_str.replace('-', '_')}.csv"
        if csv_path.exists():
            logger.info(f"Data for {date_str} already exists, skipping")
            return None

        try:
            # Get the direct URL to the raw content if possible
            # This is more robust than trying to navigate through the UI
            direct_url = f"{GITHUB_URL}/raw/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_str}.csv"

            try:
                # Try direct access to raw content first - this is the most reliable method
                logger.info(f"Trying direct access to {direct_url}")
                self.driver.get(direct_url)
                time.sleep(2)

                # Check if we got raw content
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                if body_text and "404" not in body_text and "Not Found" not in body_text:
                    logger.info("Successfully retrieved raw content directly")
                    raw_content = body_text

                    # Save raw content to file
                    with open(csv_path, 'w', encoding='utf-8') as f:
                        f.write(raw_content)

                    # Go back to the listing
                    self.driver.get(f"{GITHUB_URL}/tree/master/csse_covid_19_data/csse_covid_19_daily_reports")
                    time.sleep(2)

                    logger.info(f"Successfully scraped data for {date_str} via direct access")
                    return raw_content
                else:
                    logger.info("Direct access failed, falling back to UI navigation")
            except Exception as direct_error:
                logger.warning(f"Direct access failed: {direct_error}")

            # If direct access fails, fall back to UI navigation
            # Navigate back to the daily reports folder
            self.driver.get(f"{GITHUB_URL}/tree/master/csse_covid_19_data/csse_covid_19_daily_reports")
            time.sleep(2)

            # Try multiple approaches to find the file
            file_clicked = False

            # Approach 1: Try clicking the date file directly using various selectors
            selectors = [
                (By.XPATH, f"//a[contains(@title, '{date_str}.csv')]"),
                (By.XPATH, f"//a[contains(text(), '{date_str}.csv')]"),
                (By.XPATH, f"//a[contains(@href, '{date_str}.csv')]"),
                (By.XPATH, f"//span[contains(text(), '{date_str}.csv')]/parent::a"),
                (By.LINK_TEXT, f"{date_str}.csv"),
                (By.PARTIAL_LINK_TEXT, date_str)
            ]

            for by, selector in selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    if elements:
                        for element in elements:
                            try:
                                if date_str in element.text or date_str in element.get_attribute("href") or date_str in element.get_attribute("innerHTML"):
                                    logger.info(f"Found file element with text: {element.text}")
                                    element.click()
                                    time.sleep(2)
                                    file_clicked = True
                                    break
                            except Exception as click_error:
                                logger.warning(f"Error clicking element: {click_error}")
                                continue
                        if file_clicked:
                            break
                except Exception as selector_error:
                    logger.warning(f"File selector {selector} failed: {selector_error}")
                    continue

            # Approach 2: Use JavaScript to find and click the link
            if not file_clicked:
                try:
                    logger.info("Trying JavaScript click approach for file")
                    self.driver.execute_script(f"""
                        var links = document.querySelectorAll('a');
                        for (var i = 0; i < links.length; i++) {{
                            if (links[i].textContent.includes('{date_str}.csv') ||
                                (links[i].href && links[i].href.includes('{date_str}.csv'))) {{
                                links[i].click();
                                return true;
                            }}
                        }}
                        return false;
                    """)
                    time.sleep(2)

                    # Check if we navigated successfully
                    if date_str in self.driver.current_url:
                        file_clicked = True
                except Exception as js_error:
                    logger.warning(f"JavaScript click failed for file: {js_error}")

            # Approach 3: Try using the search functionality
            if not file_clicked:
                search_selectors = [
                    (By.CSS_SELECTOR, "button[aria-label='Search this repository']"),
                    (By.CSS_SELECTOR, "button.js-repo-search"),
                    (By.XPATH, "//button[contains(@aria-label, 'Search')]"),
                    (By.XPATH, "//summary[contains(@aria-label, 'Search')]")
                ]

                search_clicked = False
                for by, selector in search_selectors:
                    try:
                        if self._wait_and_click(by, selector):
                            search_clicked = True
                            break
                    except:
                        continue

                if search_clicked:
                    # Try multiple selectors for the search input
                    search_input = None
                    input_selectors = [
                        (By.ID, "tree-finder-field"),
                        (By.CSS_SELECTOR, "input[name='query']"),
                        (By.CSS_SELECTOR, "input[placeholder*='Search']"),
                        (By.CSS_SELECTOR, "input[type='text']")
                    ]

                    for by, selector in input_selectors:
                        try:
                            element = self._wait_for_element(by, selector)
                            if element:
                                search_input = element
                                break
                        except:
                            continue

                    if search_input:
                        search_input.clear()
                        search_input.send_keys(f"{date_str}.csv")
                        time.sleep(2)  # Wait for search results

                        # Try multiple selectors for the search results
                        result_selectors = [
                            (By.CSS_SELECTOR, "li.tree-browser-result a"),
                            (By.CSS_SELECTOR, ".js-tree-browser-result-anchor"),
                            (By.XPATH, f"//a[contains(text(), '{date_str}.csv')]"),
                            (By.XPATH, f"//a[contains(@href, '{date_str}.csv')]")
                        ]

                        for by, selector in result_selectors:
                            if self._wait_and_click(by, selector):
                                file_clicked = True
                                break

            # Approach 4: Direct navigation to the file
            if not file_clicked:
                try:
                    file_url = f"{GITHUB_URL}/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_str}.csv"
                    logger.info(f"Trying direct navigation to file: {file_url}")
                    self.driver.get(file_url)
                    time.sleep(2)
                    if date_str in self.driver.current_url:
                        file_clicked = True
                except Exception as file_error:
                    logger.warning(f"Direct file navigation failed: {file_error}")

            if not file_clicked:
                logger.warning(f"Could not find or click the file for date {date_str}")
                # Take a screenshot to help with debugging
                try:
                    screenshot_path = f"file_not_found_{date_str.replace('-', '_')}.png"
                    self.driver.save_screenshot(screenshot_path)
                    logger.info(f"Screenshot saved to {screenshot_path}")
                except:
                    pass
                return None

            # Now get the raw content - try clicking the "Raw" button
            raw_button_clicked = False
            raw_selectors = [
                (By.ID, "raw-url"),
                (By.XPATH, "//a[contains(text(), 'Raw')]"),
                (By.CSS_SELECTOR, "a.js-permalink-raw"),
                (By.CSS_SELECTOR, "a[data-testid='raw-button']"),
                (By.LINK_TEXT, "Raw")
            ]

            for by, selector in raw_selectors:
                try:
                    if self._wait_and_click(by, selector):
                        raw_button_clicked = True
                        time.sleep(2)
                        break
                except:
                    continue

            # If Raw button not found, try JavaScript
            if not raw_button_clicked:
                try:
                    logger.info("Trying JavaScript click for Raw button")
                    self.driver.execute_script("""
                        var links = document.querySelectorAll('a');
                        for (var i = 0; i < links.length; i++) {
                            if (links[i].textContent.includes('Raw') ||
                                (links[i].id && links[i].id.includes('raw-url'))) {
                                links[i].click();
                                return true;
                            }
                        }
                        return false;
                    """)
                    time.sleep(2)
                    raw_button_clicked = True
                except Exception as js_error:
                    logger.warning(f"JavaScript click for Raw button failed: {js_error}")

            # If all Raw button clicks fail, try direct URL to raw content
            if not raw_button_clicked:
                try:
                    raw_url = f"{GITHUB_URL}/raw/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_str}.csv"
                    logger.info(f"Navigating directly to raw URL: {raw_url}")
                    self.driver.get(raw_url)
                    time.sleep(2)
                    raw_button_clicked = True
                except Exception as raw_url_error:
                    logger.warning(f"Direct raw URL navigation failed: {raw_url_error}")

            if not raw_button_clicked:
                logger.warning("Could not access raw content")
                return None

            # Get the raw content - try various approaches
            raw_content = None

            # First try a pre element
            try:
                pre_element = self._wait_for_element(By.TAG_NAME, "pre")
                if pre_element:
                    raw_content = pre_element.text
            except:
                pass

            # If no pre element, try getting the body content
            if not raw_content:
                try:
                    body_element = self._wait_for_element(By.TAG_NAME, "body")
                    if body_element:
                        raw_content = body_element.text
                except:
                    pass

            # If still no content, try get the page source
            if not raw_content:
                try:
                    page_source = self.driver.page_source
                    # Simple extraction of content between body tags
                    match = re.search(r'<body[^>]*>(.*?)</body>', page_source, re.DOTALL)
                    if match:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(match.group(1), 'html.parser')
                        raw_content = soup.get_text()
                except:
                    pass

            if not raw_content:
                logger.warning("Could not extract raw content")
                return None

            # Save raw content to file
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write(raw_content)

            # Navigate back to the listing
            try:
                self.driver.get(f"{GITHUB_URL}/tree/master/csse_covid_19_data/csse_covid_19_daily_reports")
                time.sleep(2)
            except:
                pass

            logger.info(f"Successfully scraped data for {date_str}")
            return raw_content

        except Exception as e:
            logger.error(f"Error scraping data for {date_str}: {e}")
            # Try to navigate back to the listing
            try:
                self.driver.get(f"{GITHUB_URL}/tree/master/csse_covid_19_data/csse_covid_19_daily_reports")
                time.sleep(2)
            except:
                pass
            return None

    def process_csv_data(self, raw_content: str, date_str: str) -> pd.DataFrame:
        """
        Process raw CSV content into a DataFrame.
        Args:
            raw_content: Raw CSV content as string
            date_str: Date in format MM-DD-YYYY
        Returns:
            Processed DataFrame
        """
        try:
            # Parse CSV content
            df = pd.read_csv(pd.StringIO(raw_content))
            
            # Handle missing values
            for col in df.columns:
                if df[col].isnull().any():
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df[col] = df[col].fillna(0)
                    else:
                        df[col] = df[col].fillna('')
                        
            # Handle column name variations
            column_name_fixes = {
                'Case-Fatality_Ratio': 'Case_Fatality_Ratio',
                'Incident_Rate': 'Incidence_Rate',
                'Last Update': 'Last_Update'
            }
            
            df = df.rename(columns=column_name_fixes)
            
            # Convert date columns
            date_columns = ['Last_Update']
            for col in date_columns:
                if col in df.columns:
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except:
                        logger.warning(f"Failed to convert {col} to datetime")
                        
            # Add the date as a column for reference
            df['Report_Date'] = pd.to_datetime(date_str, format='%m-%d-%Y')
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing CSV data for {date_str}: {e}")
            return pd.DataFrame()

    def scrape_all_dates(self):
        """Scrape data for all dates in the range"""
        try:
            self._init_webdriver()
            
            date_range = self._get_date_range()
            if not date_range:
                logger.warning("No dates to scrape")
                return
                
            if not self.navigate_to_daily_reports():
                logger.error("Failed to navigate to daily reports, aborting")
                return
                
            all_dfs = []  # This was incorrectly written as "dfs = []" in your snippet
            
            for date_str in date_range:
                try:
                    raw_content = self.scrape_date(date_str)
                    if raw_content:
                        df = self.process_csv_data(raw_content, date_str)
                        if not df.empty:
                            all_dfs.append(df)
                            
                        # Small delay to avoid overwhelming the server
                        time.sleep(1)
                except Exception as e:
                    logger.error(f"Error processing date {date_str}: {e}")
                    continue
                    
            # Combine all DataFrames
            if all_dfs:
                self.data = pd.concat(all_dfs, ignore_index=True)
                # Save combined data
                combined_path = self.data_dir / f"covid_combined_{self.start_date.strftime('%m_%d_%Y')}_to_{self.end_date.strftime('%m_%d_%Y')}.csv"
                self.data.to_csv(combined_path, index=False)
                logger.info(f"Saved combined data to {combined_path}")
            else:
                logger.warning("No data was scraped")
                
        finally:
            self.close()

    def generate_visualizations(self, states: List[str] = None):
        """
        Generate visualizations for the specified states.

        Args:
            states: List of US states to visualize, or None for all states in the data
        """
        if self.data.empty:
            logger.warning("No data to visualize")
            return

        # Filter to only rows with confirmed cases
        data = self.data[self.data['Confirmed'] > 0].copy()

        # If no states specified, get all unique states
        if not states:
            try:
                states = data['Province_State'].unique().tolist()
            except KeyError:
                logger.error("Province_State column not found in data")
                return

        for state in states:
            try:
                # Filter data for this state
                state_data = data[data['Province_State'] == state].copy()

                if state_data.empty:
                    logger.warning(f"No data for state: {state}")
                    continue

                # Group by report date
                if 'Admin2' in state_data.columns:
                    # County-level data
                    grouped = state_data.groupby(['Report_Date', 'Admin2']).agg({
                        'Confirmed': 'sum',
                        'Deaths': 'sum',
                        'Recovered': lambda x: x.sum() if 'Recovered' in state_data.columns else 0
                    }).reset_index()

                    # Create a pivot table for counties
                    pivot = grouped.pivot(index='Report_Date', columns='Admin2', values='Confirmed')

                    # Plot county-level data
                    plt.figure(figsize=(16, 8))
                    pivot.plot(title=f"{state} COVID-19 Cases by County")
                    plt.ylabel("Confirmed Cases")
                    plt.grid(True, alpha=0.3)
                    plt.tight_layout()

                    # Save county plot
                    county_plot_path = self.graph_dir / f"{state}_counties_{self.today.strftime('%Y_%m_%d')}.png"
                    plt.savefig(county_plot_path)
                    plt.close()
                    logger.info(f"Saved county plot to {county_plot_path}")

                # Group by date for state totals
                state_totals = state_data.groupby('Report_Date').agg({
                    'Confirmed': 'sum',
                    'Deaths': 'sum',
                    'Recovered': lambda x: x.sum() if 'Recovered' in state_data.columns else 0
                })

                # Plot state totals
                plt.figure(figsize=(16, 8))
                state_totals.plot(title=f"{state} COVID-19 Trends")
                plt.ylabel("Count")
                plt.grid(True, alpha=0.3)
                plt.yscale('log')
                plt.tight_layout()

                # Save state plot
                state_plot_path = self.graph_dir / f"{state}_trends_{self.today.strftime('%Y_%m_%d')}.png"
                plt.savefig(state_plot_path)
                plt.close()
                logger.info(f"Saved state plot to {state_plot_path}")

            except Exception as e:
                logger.error(f"Error generating visualization for {state}: {e}")

    def close(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except:
                pass
            finally:
                self.driver = None

    def __del__(self):
        """Destructor to ensure WebDriver is closed"""
        self.close()


def main():
    """Main entry point"""
    # Create directories if they don't exist
    data_dir = Path("covid_data")
    graph_dir = Path("covid_graphs")
    data_dir.mkdir(exist_ok=True)
    graph_dir.mkdir(exist_ok=True)

    # Use a much smaller date range for testing
    today = date.today()
    end_date = today - timedelta(days=1)
    start_date = end_date - timedelta(days=2)  # Just scrape 2 days for testing

    # Example usage
    tracker = CovidTracker(
        start_date=start_date.strftime('%m-%d-%Y'),
        end_date=end_date.strftime('%m-%d-%Y'),
        browser="firefox",
        headless=False,  # Set to False to see the browser (helps with debugging)
        data_dir=data_dir,
        graph_dir=graph_dir,
        timeout=20  # Increase timeout for slower connections
    )

    try:
        # Add a debug message before starting
        logger.info("Starting COVID-19 data scraping process")
        logger.info(f"Browser: {tracker.browser}, Headless: {tracker.headless}")
        logger.info(f"Data directory: {tracker.data_dir}")
        logger.info(f"Graph directory: {tracker.graph_dir}")

        tracker.scrape_all_dates()

        # Check if we got any data
        if not tracker.data.empty:
            logger.info(f"Successfully scraped data with {len(tracker.data)} rows")
            tracker.generate_visualizations(states=[
                "New York",
                "California",
                "Texas",
                "Florida",
                "Washington"
            ])
        else:
            logger.warning("No data was scraped. Check the logs for errors.")

    except Exception as e:
        logger.error(f"Error in main process: {e}")
        # Print full stack trace for debugging
        import traceback
        logger.error(traceback.format_exc())
    finally:
        tracker.close()


if __name__ == "__main__":
    main()

