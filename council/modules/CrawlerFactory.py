from abc import ABC, abstractmethod
from importlib import import_module

class CrawlerFactory(ABC):

    def __init__(self, department, progress_recorder):
        self.name = department.crawler.crawler_name
        self.department = department
        self.progress_recorder = progress_recorder

    def create_crawler(self):
        module = import_module("council.crawlers.{}".format(self.name))
        crawler = getattr(module, self.name)(self.department, self.progress_recorder)
        return crawler
