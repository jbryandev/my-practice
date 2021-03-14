import re, unicodedata
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from council.modules.Crawler import Crawler

class TulsaCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("table")

    def get_page_source(self, url):
        self.progress_recorder.update(1, 20, "Opening browser instance...")
        driver = webdriver.PhantomJS()
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//*[@id='boardName']"), "{}".format(self.name))
        )
        page_source = driver.page_source
        driver.close()
        return unicodedata.normalize("NFKD", page_source)