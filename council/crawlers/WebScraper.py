from abc import ABC, abstractmethod
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import TimeoutException
from council.modules import chromedriver

class WebScraper(ABC):

    @abstractmethod
    def scrape(self):
        pass

    @staticmethod
    def request(url, timeout):
        return requests.get(url, timeout=timeout)

    @staticmethod
    def get_soup(page_source, **kwargs):
        return BeautifulSoup(page_source, "html.parser", **kwargs)

class SimpleScraper(WebScraper):

    def scrape(self, url, strainer=None, timeout=10):
        super().scrape()
        response = self.request(url, timeout)
        self.progress_observer.update(1, 10, "Connection succeeded. Getting current list of agendas...", 2)
        if strainer:
            soup = self.get_soup(response.text, parse_only=strainer)
        else:
            soup = self.get_soup(response.text)
        return soup

class SeleniumScraper(WebScraper):

    def scrape(self, url, strainer=None, timeout=10):
        super().scrape()
        browser = chromedriver.open_browser(url)
        self.progress_observer.update(1, 10, "Connection succeeded. Getting current list of agendas...", 2)
        try:
            WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name('body'))
            if strainer:
                soup = self.get_soup(browser.page_source, parse_only=strainer)
            else:
                soup = self.get_soup(browser.page_source)
            browser.quit()
            return soup
        except TimeoutException:
            print("Timed out waiting for page to load")
            browser.quit()

class TulsaScraper(WebScraper):

    def scrape(self, url, strainer=None, timeout=10):
        super().scrape()
        browser = chromedriver.open_browser(url)
        self.progress_observer.update(1, 10, "Connection succeeded. Getting current list of agendas...", 2)
        try:
            WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name("iframe"))
            browser.switch_to.frame(browser.find_element_by_tag_name("iframe"))
            current_month = str(datetime.now().strftime("%B"))
            current_year = str(datetime.now().year)
            month_select = Select(browser.find_element_by_name("MeetingMonth"))
            month_select.select_by_visible_text(current_month)
            year_select = Select(browser.find_element_by_name("MeetingYear"))
            year_select.select_by_visible_text(current_year)
            browser.find_element_by_name("Submit").click()
            WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name("table"))
            if strainer:
                soup = self.get_soup(browser.page_source, parse_only=strainer)
            else:
                soup = self.get_soup(browser.page_source)
            browser.quit()
            return soup
        except TimeoutException:
            print("Timed out waiting for page to load")
            browser.quit()
