from council.crawlers import edmond, el_reno, lawton, \
    midwest_city, moore, norman, okc, tulsa

class CrawlerFactory:

    def __init__(self, crawler, progress_recorder):
        self.crawler = crawler
        self.progress_recorder = progress_recorder
    
    def create_crawler(self):
        name = self.crawler.name

        if name == "Edmond":
            return edmond.EdmondCrawler(self.progress_recorder)