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
    print("set_chrome_options_called")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    # This prevents unpacked extensions error dialog box from popping up
    chrome_options.add_experimental_option("useAutomationExtension", False)
    print(type(chrome_options))
    return chrome_options

def get_chrome_driver(chrome_options):
    """
    This function takes chrome options and establishes the driver.
    """
    driver = webdriver.Chrome(
        executable_path=os.environ.get("CHROMEDRIVER_PATH"),
        chrome_options=chrome_options
    )

    return driver
