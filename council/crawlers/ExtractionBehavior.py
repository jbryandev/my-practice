import requests
from abc import ABC, abstractmethod
from council.modules.backend import set_progress
from bs4 import BeautifulSoup, SoupStrainer

class ExtractionBehavior(ABC):

    @abstractmethod
    def extract(self):
        pass

    @staticmethod
    def request(url, timeout=10):
        return requests.get(url, timeout=timeout)
    
    @staticmethod
    def get_soup(page_source, **kwargs):
        return BeautifulSoup(page_source, "html.parser", **kwargs)

class BaseExtractionBehavor(ExtractionBehavior):

    def extract(self, url, strainer, progress_recorder):
        # Request City agenda website
        set_progress(progress_recorder, 0, 10, "Connecting to City website...")
        response = self.request(url)

        # Extract HTML with BeautifulSoup
        set_progress(progress_recorder, 1, 10, "Connection succeeded. Getting current list of agendas...", 2)
        soup = self.get_soup(response.text, strainer)
        return soup

class SeleniumExtractionBehavor(ExtractionBehavior):

    def extract(self, url, strainer, progress_recorder):
        pass