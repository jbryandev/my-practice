from abc import ABC, abstractmethod
from bs4 import SoupStrainer

class Strainer(ABC):

    def __init__(self):
        pass

class EdmondStrainer(Strainer):

    def __init__(self):
        self.strainer = SoupStrainer("tbody", class_="nowrap smallText")

class ElRenoStrainer(Strainer):

    def __init__(self):
        self.strainer = SoupStrainer("div", class_="javelin_regionContent")

class OKCStrainer(Strainer):

    def __init__(self):
        self.strainer = SoupStrainer("tr", class_="public_meeting")
