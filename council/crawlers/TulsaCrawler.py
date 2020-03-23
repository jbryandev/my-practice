from bs4 import SoupStrainer
from council.crawlers.crawler import Crawler

class TulsaCrawler(Crawler):

    def strainer(self):
        return SoupStrainer("table")
