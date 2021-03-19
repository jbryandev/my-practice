"""
This module sets options for Chromedriver and establishes
the driver with the specified options
"""
import os
from selenium import webdriver

def set_chrome_options():
    """
    This function sets the chrome options for the driver.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("CHROME_PATH")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36")
    chrome_options.add_experimental_option("useAutomationExtension", False) # Avoids unpacked extensions error dialog box
    chrome_options.add_experimental_option("excludeSwitches", ['enable-logging', 'enable-automation']) # Silences devtools listening alert

    return chrome_options

def get_chrome_driver(chrome_options):
    """
    This function takes chrome options and establishes the driver.
    """
    driver = webdriver.Chrome(
        executable_path=os.environ.get("CHROMEDRIVER_PATH"),
        options=chrome_options
    )

    return driver

def open_browser(page_url):
    """
    This function uses Selenium to open a Chrome browser instance and
    navigate to the given URL.
    """
    chrome_options = set_chrome_options()
    browser = get_chrome_driver(chrome_options)
    browser.get(page_url)

    return browser
